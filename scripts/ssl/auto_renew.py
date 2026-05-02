#!/usr/bin/env python3
"""
Fully automated SSL renewal — DNS-01 challenge with GoDaddy DNS API.

Designed to run in GitHub Actions on a schedule. Requires these env vars:
    GODADDY_API_KEY       - GoDaddy production API key
    GODADDY_API_SECRET    - GoDaddy production API secret
    LE_ACCOUNT_KEY_PEM    - (optional) PEM-encoded Let's Encrypt account key.
                            If absent, a new account is created and the key is
                            written to stdout for you to copy into a secret.
    LE_EMAIL              - (optional) account email (default: hardcoded below)

On success, writes:
    output/privkey.pem
    output/cert.pem
    output/chain.pem
    output/fullchain.pem

Exit codes:
    0 — cert issued
    1 — error
    2 — current cert is still valid for >=RENEW_THRESHOLD_DAYS, no renewal needed
"""
import datetime
import os
import socket
import ssl
import sys
import time
from pathlib import Path

import requests
from acme import client, messages, challenges, crypto_util, errors as acme_errors
import josepy as jose
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# -------- config --------
DOMAINS = ["sdts.org", "www.sdts.org", "bts.sdts.org", "www.bts.sdts.org"]
APEX_DOMAINS = {"sdts.org"}      # the registered domains we own at GoDaddy
DEFAULT_EMAIL = "udhayakumar.d@gmail.com"
DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
USER_AGENT = "sdts-ssl-renewal/1.0"
RENEW_THRESHOLD_DAYS = 30        # only renew if existing cert expires within this window
GODADDY_API = "https://api.godaddy.com/v1"
DNS_PROPAGATION_WAIT = 30        # seconds to wait after creating TXT record

OUT_DIR = Path(os.environ.get("SSL_OUT_DIR", "output"))
OUT_DIR.mkdir(parents=True, exist_ok=True)


# -------- helpers --------
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_live_cert_expiry(host, port=443, timeout=10):
    """Return notAfter as datetime, or None if cannot fetch."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                der = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(der, default_backend())
                return cert.not_valid_after_utc.replace(tzinfo=None)
    except Exception as e:
        log(f"could not fetch live cert from {host}: {e}")
        return None


def days_until_expiry():
    """Return min days until expiry across DOMAINS, or None if can't determine."""
    expiries = []
    for d in DOMAINS:
        exp = fetch_live_cert_expiry(d)
        if exp:
            days = (exp - datetime.datetime.utcnow()).days
            log(f"  {d}: expires in {days} days ({exp.isoformat()})")
            expiries.append(days)
    return min(expiries) if expiries else None


def godaddy_get_apex(fqdn):
    """Return the apex (registered) domain for a given FQDN."""
    for apex in APEX_DOMAINS:
        if fqdn == apex or fqdn.endswith("." + apex):
            return apex
    raise ValueError(f"No apex domain configured for {fqdn}")


def godaddy_record_name(fqdn):
    """Return the record name (relative to apex) for an _acme-challenge TXT."""
    apex = godaddy_get_apex(fqdn)
    if fqdn == apex:
        return "_acme-challenge"
    sub = fqdn[: -(len(apex) + 1)]   # strip ".sdts.org"
    return f"_acme-challenge.{sub}"


def godaddy_headers(api_key, api_secret):
    return {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def godaddy_put_txt(api_key, api_secret, fqdn, value):
    """PUT (replace) all TXT records at name to a single record with value."""
    apex = godaddy_get_apex(fqdn)
    name = godaddy_record_name(fqdn)
    url = f"{GODADDY_API}/domains/{apex}/records/TXT/{name}"
    payload = [{"data": value, "ttl": 600}]
    r = requests.put(url, headers=godaddy_headers(api_key, api_secret), json=payload, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"GoDaddy PUT {url} failed: {r.status_code} {r.text}")
    log(f"  {fqdn}: TXT record set ({name}.{apex} = {value[:12]}...)")


def godaddy_delete_txt(api_key, api_secret, fqdn):
    """Best-effort delete of TXT records for the challenge name."""
    apex = godaddy_get_apex(fqdn)
    name = godaddy_record_name(fqdn)
    url = f"{GODADDY_API}/domains/{apex}/records/TXT/{name}"
    try:
        r = requests.delete(url, headers=godaddy_headers(api_key, api_secret), timeout=30)
        if r.status_code < 400:
            log(f"  {fqdn}: TXT record deleted")
        else:
            log(f"  {fqdn}: TXT delete returned {r.status_code} (non-fatal)")
    except Exception as e:
        log(f"  {fqdn}: TXT delete failed (non-fatal): {e}")


# -------- main --------
def main():
    api_key = os.environ.get("GODADDY_API_KEY")
    api_secret = os.environ.get("GODADDY_API_SECRET")
    if not api_key or not api_secret:
        print("[!] GODADDY_API_KEY and GODADDY_API_SECRET must be set", file=sys.stderr)
        sys.exit(1)

    email = os.environ.get("LE_EMAIL", DEFAULT_EMAIL)

    force_renew = os.environ.get("FORCE_RENEW", "").lower() == "true"

    if force_renew:
        log("FORCE_RENEW=true — skipping expiry check, proceeding with renewal")
    else:
        log("Checking current cert expiry on live domains")
        days = days_until_expiry()
        if days is not None and days >= RENEW_THRESHOLD_DAYS:
            log(f"All domains valid for >={RENEW_THRESHOLD_DAYS} days. No renewal needed.")
            sys.exit(2)
        if days is None:
            log("Could not determine current expiry — proceeding with renewal anyway")
        else:
            log(f"At least one domain expires within {RENEW_THRESHOLD_DAYS} days — renewing")

    # ---- account key ----
    acct_key_pem = os.environ.get("LE_ACCOUNT_KEY_PEM")
    if acct_key_pem:
        log("Using account key from LE_ACCOUNT_KEY_PEM")
        acct_key = serialization.load_pem_private_key(acct_key_pem.encode(), password=None)
    else:
        log("Generating new account key (save it as LE_ACCOUNT_KEY_PEM secret!)")
        acct_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        new_pem = acct_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        banner = "#" * 72
        print(f"\n{banner}")
        print("##  SAVE THIS AS GitHub SECRET 'LE_ACCOUNT_KEY_PEM'              ##")
        print("##  Copy the PEM block (BEGIN ... END lines inclusive) into       ##")
        print("##  Settings > Secrets > Actions > New secret: LE_ACCOUNT_KEY_PEM ##")
        print(f"{banner}\n")
        print(new_pem)
        print(f"\n{banner}")
        print("##  END LE_ACCOUNT_KEY_PEM — also saved to artifact zip below     ##")
        print(f"{banner}\n")
        # Also write to artifact so it can be retrieved from the run's zip
        (OUT_DIR / "LE_ACCOUNT_KEY_PEM.secret.txt").write_text(new_pem)

    # ---- ACME client ----
    jwk = jose.JWKRSA(key=jose.ComparableRSAKey(acct_key))
    net = client.ClientNetwork(jwk, user_agent=USER_AGENT)
    directory = client.ClientV2.get_directory(DIRECTORY_URL, net)
    acme = client.ClientV2(directory, net=net)

    log("Registering / fetching Let's Encrypt account")
    try:
        regr = acme.new_account(messages.NewRegistration.from_data(email=email, terms_of_service_agreed=True))
    except acme_errors.ConflictError as e:
        log(f"Account exists: {e.location}")
        regr = messages.RegistrationResource(uri=e.location, body=messages.Registration())
        regr = acme.query_registration(regr)
    net.account = regr

    # ---- domain key + CSR ----
    log("Generating domain private key")
    domain_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    domain_key_pem = domain_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    (OUT_DIR / "privkey.pem").write_bytes(domain_key_pem)

    log(f"Building CSR for {', '.join(DOMAINS)}")
    csr_pem = crypto_util.make_csr(domain_key_pem, DOMAINS)

    log("Submitting order")
    order = acme.new_order(csr_pem)

    # ---- DNS-01 challenges ----
    dns_records_set = []
    try:
        log("Setting DNS TXT records via GoDaddy API")
        challenge_data = []
        for auth in order.authorizations:
            domain = auth.body.identifier.value
            dns_chall = next((c for c in auth.body.challenges if isinstance(c.chall, challenges.DNS01)), None)
            if dns_chall is None:
                raise RuntimeError(f"No DNS-01 challenge for {domain}")
            response, validation = dns_chall.response_and_validation(jwk)
            godaddy_put_txt(api_key, api_secret, domain, validation)
            dns_records_set.append(domain)
            challenge_data.append({"auth": auth, "challb": dns_chall, "response": response})

        log(f"Waiting {DNS_PROPAGATION_WAIT}s for DNS propagation")
        time.sleep(DNS_PROPAGATION_WAIT)

        log("Triggering validation for each authorization")
        for cd in challenge_data:
            acme.answer_challenge(cd["challb"], cd["response"])

        log("Polling order until finalized (up to 180 sec)")
        try:
            final = acme.poll_and_finalize(
                order,
                deadline=datetime.datetime.now() + datetime.timedelta(seconds=180),
            )
        except acme_errors.ValidationError as e:
            print("[!] Validation failed:", file=sys.stderr)
            for failed in e.failed_authzrs:
                for ch in failed.body.challenges:
                    if ch.error:
                        print(f"    {failed.body.identifier.value}: {ch.error}", file=sys.stderr)
            sys.exit(1)
    finally:
        log("Cleaning up DNS TXT records")
        for d in dns_records_set:
            godaddy_delete_txt(api_key, api_secret, d)

    # ---- save outputs ----
    fullchain = final.fullchain_pem
    parts, buf = [], []
    for line in fullchain.splitlines(keepends=True):
        buf.append(line)
        if "-----END CERTIFICATE-----" in line:
            parts.append("".join(buf))
            buf = []

    (OUT_DIR / "fullchain.pem").write_text(fullchain)
    (OUT_DIR / "cert.pem").write_text(parts[0])
    (OUT_DIR / "chain.pem").write_text("".join(parts[1:]))

    log("SUCCESS — files written to " + str(OUT_DIR))
    for name in ("privkey.pem", "cert.pem", "chain.pem", "fullchain.pem"):
        p = OUT_DIR / name
        log(f"  {name}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
