# SSL certificate renewal runbook

This document explains how SDTS gets its HTTPS certificate, how it's renewed, and what to do if something breaks. Read it once before the cert expires; re-read it when GitHub opens an "Install new SSL cert" issue.

## What's installed

A single Let's Encrypt SAN certificate covering four hostnames:

- `sdts.org`
- `www.sdts.org`
- `bts.sdts.org`
- `www.bts.sdts.org`

Hosting: **GoDaddy shared hosting (Plesk Obsidian)**. There is no SSH access and no Plesk Let's Encrypt extension on this plan, which is why renewal is not built into Plesk.

Cert lifetime: **90 days**. We renew when fewer than 30 days remain.

## How renewal happens (normal path)

Every Monday at 12:00 UTC, the [`ssl-renew`](../.github/workflows/ssl-renew.yml) workflow:

1. Reads the live cert on each of the 4 domains.
2. If any of them expire within 30 days, it runs [`scripts/ssl/auto_renew.py`](../scripts/ssl/auto_renew.py).
3. That script asks Let's Encrypt for a new cert using a **DNS-01 challenge**: it adds a TXT record to each domain via the GoDaddy DNS API, waits for propagation, lets LE verify it, then deletes the TXT record.
4. The resulting cert files are uploaded as a workflow artifact named `ssl-cert-<run number>`.
5. A GitHub issue titled "Install new SSL cert (run #...)" is opened automatically with download + install instructions.

A separate workflow, [`ssl-expiry-check`](../.github/workflows/ssl-expiry-check.yml), runs **daily** and opens a louder warning issue if anything expires within 14 days. This is a backstop in case `ssl-renew` fails silently.

## Your job when the issue is opened

This takes 5 minutes.

1. **Download the artifact** linked in the issue. It contains:
   - `privkey.pem` — the private key
   - `cert.pem` — the certificate
   - `chain.pem` — the Let's Encrypt intermediate CA
   - `fullchain.pem` — cert + chain combined (not needed for Plesk)

2. **Log in to Plesk** at https://a2nwvpweb053.shr.prod.iad2.secureserver.net:8443 (or whatever the current GoDaddy Plesk URL is — find it via "Manage" in your GoDaddy account).

3. For **sdts.org**:
   - Websites & Domains → click `sdts.org` → **SSL/TLS Certificates**
   - Click **Add SSL/TLS Certificate**
   - **Certificate name:** `letsencrypt_YYYY-MM-DD` (today's date)
   - Open `privkey.pem` in a text editor, copy everything (including the `-----BEGIN/END-----` lines), paste into the **Private key** field
   - Open `cert.pem`, copy everything, paste into the **Certificate** field
   - Open `chain.pem`, copy everything, paste into the **CA certificate** field
   - Click **Upload Certificate**
   - Go back to Websites & Domains → `sdts.org` → **Hosting Settings** → scroll to **Security** → choose your new cert from the **Certificate** dropdown → click OK.

4. Repeat step 3 for **bts.sdts.org**. Same cert, just selected on the bts.sdts.org domain.

5. Verify in a browser (use incognito to bypass any cache):
   - https://sdts.org
   - https://www.sdts.org
   - https://bts.sdts.org
   - https://www.bts.sdts.org

   All four should show a valid padlock and the cert expiry should be ~90 days out. You can also check at https://www.ssllabs.com/ssltest/.

6. Close the GitHub issue.

7. After a few days, you can delete the **previous** cert from Plesk's SSL/TLS Certificates list to keep it tidy. Don't delete the one currently in use!

## One-time setup (already done — recorded for future audits)

These secrets are stored in the repo's GitHub Actions secrets:

| Secret name | What it is | How to get it |
|---|---|---|
| `GODADDY_API_KEY` | GoDaddy DNS API key (production tier) | https://developer.godaddy.com/keys |
| `GODADDY_API_SECRET` | Pairs with the API key above | Same page |
| `LE_ACCOUNT_KEY_PEM` | Let's Encrypt account private key (PKCS8 PEM) | Generated automatically on first run; the run logs print it for you to copy into a secret |
| `LE_EMAIL` (optional) | Email LE uses for expiration notices | Hand-set when secrets are configured |

If `LE_ACCOUNT_KEY_PEM` is missing, the first run of `auto_renew.py` will create one and print it to the workflow log so you can paste it into the secret. Subsequent runs reuse it.

## Manual renewal (fallback)

If the GoDaddy API is down, or the auto workflow fails for some reason and the cert is expiring TODAY, use the manual flow on a Mac/Linux machine:

```bash
cd scripts/ssl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manual_phase1.py
# This prints 4 challenge files. For each one:
#   - In Plesk file manager, navigate to:
#       httpdocs/.well-known/acme-challenge/         (for sdts.org and www.sdts.org)
#       bts.sdts.org/.well-known/acme-challenge/    (for bts.sdts.org and www.bts.sdts.org)
#   - Create a file with the printed filename. NO EXTENSION (Plesk sometimes adds .txt — rename if it does).
#   - Paste the printed content as the file body.
# Then verify in a browser that each "Verify URL" works over plain http (not https).

python manual_phase2.py
# Validates each challenge with Let's Encrypt and downloads the cert.
# Output files go into scripts/ssl/ : privkey.pem, cert.pem, chain.pem, fullchain.pem.
```

Then install in Plesk exactly as described above.

## Troubleshooting

**"Validation FAILED" from `manual_phase2.py` or `auto_renew.py`**
Means Let's Encrypt couldn't read one of the challenges. For HTTP-01: open each "Verify URL" in a browser — it must return the exact token text, not a redirect, not an error page, not HTTPS. For DNS-01: query the TXT record from a public DNS resolver (`dig _acme-challenge.sdts.org TXT @8.8.8.8`) and confirm the value matches what `auto_renew.py` set.

**"too many failed authorizations recently"**
Let's Encrypt rate-limits you to 5 failed validations per hostname per hour. Wait an hour and retry. To avoid this, **always** verify the challenges are publicly reachable BEFORE pressing Enter or letting the script trigger validation.

**Plesk file manager added `.txt` to the challenge filename**
Open the file in Plesk file manager and use Rename to remove the extension. The filename must be exactly the token string with nothing after it.

**The auto-renew workflow keeps failing with a GoDaddy API error**
The API key may have expired or been revoked. Generate a new one at https://developer.godaddy.com/keys (the production tier, not OTE) and update the `GODADDY_API_KEY` and `GODADDY_API_SECRET` secrets.

**The cert installed in Plesk but the browser still shows the old one**
Plesk sometimes needs the domain's hosting settings explicitly re-saved. Go to Hosting Settings for the domain, re-select the cert from the dropdown, click OK. If still wrong, try a hard refresh in the browser (Cmd+Shift+R).

**The `LE_ACCOUNT_KEY_PEM` secret is lost / unrecoverable**
You can regenerate it. Delete the `LE_ACCOUNT_KEY_PEM` secret, run the workflow manually with `force=true`, copy the new key from the run log into a new `LE_ACCOUNT_KEY_PEM` secret. There's no penalty — Let's Encrypt allows multiple accounts.

## Why this design

- **Free.** Every component (Let's Encrypt, GitHub Actions on a public repo, GoDaddy DNS API) costs $0.
- **Survives team turnover.** New volunteers don't need to know anything except "open the issue, follow the instructions." No Slack bus-factor risk.
- **Loud failure.** If anything breaks, GitHub opens an issue. No silent expiry → broken site for users.
- **Manual install of cert.** We deliberately do NOT push the new cert into Plesk via the Plesk API, because (a) GoDaddy shared Plesk doesn't reliably expose API access, and (b) requiring a human to click "Upload Certificate" means a real person notices that renewal happened and verifies the site still works. Nine times out of ten this trade is the right one for a small nonprofit.
