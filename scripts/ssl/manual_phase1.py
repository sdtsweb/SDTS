#!/usr/bin/env python3
"""
Manual SSL renewal — Phase 1 (HTTP-01 challenge).

Use this when GoDaddy DNS API is not configured (or as a fallback).
This script registers/looks-up the Let's Encrypt account, places an order
for sdts.org / www.sdts.org / bts.sdts.org / www.bts.sdts.org, and prints
the four challenge files you need to upload via Plesk file manager.

Usage:
    pip install -r requirements.txt
    python manual_phase1.py
    # ...upload the 4 files to your server via Plesk...
    python manual_phase2.py
"""
import json
import sys
from pathlib import Path

from acme import client, messages, challenges, crypto_util, errors as acme_errors
import josepy as jose
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

DIR = Path(__file__).resolve().parent
STATE = DIR / "state.json"
DOMAINS = ["sdts.org", "www.sdts.org", "bts.sdts.org", "www.bts.sdts.org"]
EMAIL = "udhayakumar.d@gmail.com"   # change to a team mailing list when handing off
DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
USER_AGENT = "sdts-ssl-renewal/1.0"

# ---------- account key ----------
acct_key_path = DIR / "account.key"
if acct_key_path.exists():
    print("[*] Reusing existing account key")
    acct_key = serialization.load_pem_private_key(acct_key_path.read_bytes(), password=None)
else:
    print("[*] Generating new account key (will be saved to account.key — keep it!)")
    acct_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    acct_key_path.write_bytes(acct_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))

# ---------- ACME client ----------
jwk = jose.JWKRSA(key=jose.ComparableRSAKey(acct_key))
net = client.ClientNetwork(jwk, user_agent=USER_AGENT)
directory = client.ClientV2.get_directory(DIRECTORY_URL, net)
acme = client.ClientV2(directory, net=net)

print("[*] Registering / fetching Let's Encrypt account")
try:
    regr = acme.new_account(messages.NewRegistration.from_data(email=EMAIL, terms_of_service_agreed=True))
except acme_errors.ConflictError as e:
    print(f"[*] Account exists: {e.location}")
    regr = messages.RegistrationResource(uri=e.location, body=messages.Registration())
    regr = acme.query_registration(regr)
net.account = regr
print(f"[*] Account: {regr.uri}")

# ---------- domain key + CSR ----------
print("[*] Generating new domain private key")
domain_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
domain_key_pem = domain_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)
(DIR / "privkey.pem").write_bytes(domain_key_pem)

print(f"[*] Building CSR for: {', '.join(DOMAINS)}")
csr_pem = crypto_util.make_csr(domain_key_pem, DOMAINS)

print("[*] Submitting order to Let's Encrypt")
order = acme.new_order(csr_pem)

# ---------- collect HTTP-01 challenges ----------
chall_info = []
for auth in order.authorizations:
    domain = auth.body.identifier.value
    http = next(c for c in auth.body.challenges if isinstance(c.chall, challenges.HTTP01))
    response, validation = http.response_and_validation(jwk)
    chall_info.append({
        "domain": domain,
        "filename": http.chall.encode("token"),
        "content": validation,
        "url": f"http://{domain}/.well-known/acme-challenge/{http.chall.encode('token')}",
        "auth_uri": auth.uri,
        "challb_uri": http.uri,
    })

# ---------- save state ----------
state = {
    "acct_uri": regr.uri,
    "acct_key_path": str(acct_key_path),
    "order_uri": order.uri,
    "finalize_uri": order.body.finalize,
    "csr_pem": csr_pem.decode() if isinstance(csr_pem, bytes) else csr_pem,
    "challenges": chall_info,
}
STATE.write_text(json.dumps(state, indent=2))

# ---------- print upload instructions ----------
print()
print("=" * 76)
print("UPLOAD THESE 4 CHALLENGE FILES VIA PLESK FILE MANAGER")
print("=" * 76)
print("""
For sdts.org and www.sdts.org:  put files in  httpdocs/.well-known/acme-challenge/
For bts.sdts.org and www.bts.sdts.org:  put files in  bts.sdts.org/.well-known/acme-challenge/

Each file must have NO extension (Plesk's "Create File" sometimes adds .txt — rename it!)
""")
for c in chall_info:
    print(f"\n  Domain:   {c['domain']}")
    print(f"  Filename: {c['filename']}")
    print(f"  Content:  {c['content']}")
    print(f"  Verify:   {c['url']}")
print()
print("=" * 76)
print("Once all 4 are uploaded, verify each URL in your browser, then run:")
print("    python manual_phase2.py")
print("=" * 76)
