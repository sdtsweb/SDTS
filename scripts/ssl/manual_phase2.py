#!/usr/bin/env python3
"""
Manual SSL renewal — Phase 2 (HTTP-01 challenge).

Run this AFTER you have uploaded the 4 challenge files printed by manual_phase1.py.
This triggers Let's Encrypt to validate each file, finalizes the order, and
saves cert.pem / chain.pem / fullchain.pem (privkey.pem was saved in phase 1).

Then paste privkey.pem + cert.pem + chain.pem into Plesk's
"Add SSL/TLS Certificate" form for each domain.
"""
import datetime
import json
import sys
from pathlib import Path

from acme import client, messages, challenges, errors as acme_errors
import josepy as jose
from cryptography.hazmat.primitives import serialization

DIR = Path(__file__).resolve().parent
STATE = DIR / "state.json"
DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
USER_AGENT = "sdts-ssl-renewal/1.0"

if not STATE.exists():
    print(f"[!] state.json not found. Run manual_phase1.py first.", file=sys.stderr)
    sys.exit(1)

state = json.loads(STATE.read_text())

# ---------- reconstruct ACME client ----------
acct_key = serialization.load_pem_private_key(
    Path(state["acct_key_path"]).read_bytes(), password=None
)
jwk = jose.JWKRSA(key=jose.ComparableRSAKey(acct_key))
regr = messages.RegistrationResource(uri=state["acct_uri"], body=messages.Registration())
net = client.ClientNetwork(jwk, account=regr, user_agent=USER_AGENT)
directory = client.ClientV2.get_directory(DIRECTORY_URL, net)
acme = client.ClientV2(directory, net=net)

# ---------- re-fetch order + authorizations ----------
print(f"[*] Fetching order")
resp = acme._post_as_get(state["order_uri"])
order_body = messages.Order.from_json(resp.json())

authzs = []
for auth_uri in order_body.authorizations:
    r = acme._post_as_get(auth_uri)
    body = messages.Authorization.from_json(r.json())
    authzs.append(messages.AuthorizationResource(uri=auth_uri, body=body))
    print(f"    {body.identifier.value}: status={body.status}")

order_resource = messages.OrderResource(
    uri=state["order_uri"],
    body=order_body,
    authorizations=authzs,
    csr_pem=state["csr_pem"].encode(),
)

# ---------- trigger validation ----------
print("\n[*] Triggering HTTP-01 challenges")
for authz in authzs:
    if authz.body.status == messages.STATUS_VALID:
        print(f"    {authz.body.identifier.value}: already valid, skipping")
        continue
    http = next(c for c in authz.body.challenges if isinstance(c.chall, challenges.HTTP01))
    response, _ = http.response_and_validation(jwk)
    acme.answer_challenge(http, response)
    print(f"    {authz.body.identifier.value}: triggered")

# ---------- poll + finalize ----------
print("\n[*] Polling order until finalized (up to 120 sec)")
try:
    final = acme.poll_and_finalize(
        order_resource,
        deadline=datetime.datetime.now() + datetime.timedelta(seconds=120),
    )
except acme_errors.ValidationError as e:
    print("[!] Validation FAILED — Let's Encrypt could not reach one or more files.")
    for failed in e.failed_authzrs:
        for ch in failed.body.challenges:
            if ch.error:
                print(f"    {failed.body.identifier.value}: {ch.error}")
    print("\nDouble-check that all 4 URLs are publicly reachable over plain HTTP, then")
    print("re-run manual_phase1.py to start a new order with fresh tokens.")
    sys.exit(1)

# ---------- split chain into separate files ----------
fullchain = final.fullchain_pem
parts, buf = [], []
for line in fullchain.splitlines(keepends=True):
    buf.append(line)
    if "-----END CERTIFICATE-----" in line:
        parts.append("".join(buf))
        buf = []
leaf = parts[0]
chain = "".join(parts[1:])

(DIR / "fullchain.pem").write_text(fullchain)
(DIR / "cert.pem").write_text(leaf)
(DIR / "chain.pem").write_text(chain)

# ---------- success ----------
print("\n" + "=" * 76)
print("SUCCESS — certificate issued for:")
for c in state["challenges"]:
    print(f"    - {c['domain']}")
print("=" * 76)
print(f"\nFiles written in {DIR}:")
for name in ("privkey.pem", "cert.pem", "chain.pem", "fullchain.pem"):
    p = DIR / name
    print(f"    {name:18s}  {p.stat().st_size:>5d} bytes")
print("\nNext step: install in Plesk — see docs/SSL_RENEWAL.md")
