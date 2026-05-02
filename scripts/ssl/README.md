# SSL renewal scripts

Scripts that renew the Let's Encrypt SSL certificate covering:

- sdts.org
- www.sdts.org
- bts.sdts.org
- www.bts.sdts.org

Two flows are provided. **Use the automated flow.** The manual flow exists only as a fallback if the GoDaddy API is unavailable.

## Setup (one-time)

```bash
cd scripts/ssl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Automated flow (recommended)

`auto_renew.py` uses the **DNS-01** challenge with the GoDaddy DNS API. It runs unattended in GitHub Actions on a schedule. See `.github/workflows/ssl-renew.yml`.

To run it locally for testing, set environment variables:

```bash
export GODADDY_API_KEY=...
export GODADDY_API_SECRET=...
export LE_ACCOUNT_KEY_PEM="$(cat account.key)"   # optional; created on first run if missing
python auto_renew.py
```

Outputs go to `output/` (privkey.pem, cert.pem, chain.pem, fullchain.pem).

## Manual flow (fallback)

If the GoDaddy API is broken or unavailable:

```bash
python manual_phase1.py     # prints 4 challenge files to upload
# upload them via Plesk, verify each URL is publicly reachable
python manual_phase2.py     # validates + downloads cert
```

See `docs/SSL_RENEWAL.md` for the full step-by-step including Plesk install instructions.

## Files

| File | Purpose |
|---|---|
| `auto_renew.py` | Automated DNS-01 renewal via GoDaddy API |
| `manual_phase1.py` | Manual HTTP-01: place order, print challenges |
| `manual_phase2.py` | Manual HTTP-01: validate + download cert |
| `check_expiry.py` | Read live cert expiry, write to GITHUB_OUTPUT |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Don't commit private keys or generated certs |

## What gets generated

After a successful run you have four PEM files:

| File | What it is | Where to paste in Plesk |
|---|---|---|
| `privkey.pem` | Private key (KEEP SECRET) | "Private key" box |
| `cert.pem` | Leaf certificate | "Certificate" box |
| `chain.pem` | Let's Encrypt intermediate CA | "CA certificate" box |
| `fullchain.pem` | cert + chain combined | (not needed for Plesk) |
