# How to drop this into the SDTS repo

This package contains 7 files that go into specific paths in `sdtsweb/SDTS`.

## File map

```
sdts-ssl-package/                                    →  SDTS/
├── docs/SSL_RENEWAL.md                              →  docs/SSL_RENEWAL.md
├── scripts/ssl/auto_renew.py                        →  scripts/ssl/auto_renew.py
├── scripts/ssl/manual_phase1.py                     →  scripts/ssl/manual_phase1.py
├── scripts/ssl/manual_phase2.py                     →  scripts/ssl/manual_phase2.py
├── scripts/ssl/check_expiry.py                      →  scripts/ssl/check_expiry.py
├── scripts/ssl/requirements.txt                     →  scripts/ssl/requirements.txt
├── scripts/ssl/.gitignore                           →  scripts/ssl/.gitignore
├── scripts/ssl/README.md                            →  scripts/ssl/README.md
├── .github/workflows/ssl-renew.yml                  →  .github/workflows/ssl-renew.yml
└── .github/workflows/ssl-expiry-check.yml           →  .github/workflows/ssl-expiry-check.yml
```

## Steps to install

```bash
# 1. Clone your repo
git clone https://github.com/sdtsweb/SDTS.git
cd SDTS

# 2. Copy this package's contents into the repo (preserves the directory layout)
cp -R /path/to/sdts-ssl-package/* .
cp -R /path/to/sdts-ssl-package/.github .

# 3. Verify the structure
ls docs/SSL_RENEWAL.md
ls scripts/ssl/
ls .github/workflows/

# 4. Commit and push
git add docs/SSL_RENEWAL.md scripts/ssl/ .github/workflows/ssl-renew.yml .github/workflows/ssl-expiry-check.yml INSTALL.md
git commit -m "Add SSL renewal automation and runbook"
git push
```

## After pushing, set up the GitHub Secrets

Go to: **https://github.com/sdtsweb/SDTS/settings/secrets/actions**

Click **New repository secret** for each:

| Name | Value |
|---|---|
| `GODADDY_API_KEY` | From https://developer.godaddy.com/keys (Production tier, not OTE) |
| `GODADDY_API_SECRET` | Pairs with the API key above |
| `LE_EMAIL` | Email for Let's Encrypt account (e.g. udhayakumar.d@gmail.com) |
| `LE_ACCOUNT_KEY_PEM` | (skip for now — first workflow run will print one for you to copy in) |

## First test run

After secrets are set:

1. Go to **Actions** tab → **SSL renew** workflow → **Run workflow** → set `force` to `true` → Run.
2. Wait for it to complete (~2 minutes).
3. The first run will print a new Let's Encrypt account key in the logs (look for `>>> SAVE THIS AS GitHub SECRET 'LE_ACCOUNT_KEY_PEM' <<<`). Copy that block (everything between BEGIN and END markers) into a new `LE_ACCOUNT_KEY_PEM` secret.
4. Download the artifact, install the cert in Plesk per the runbook.
5. The next time the workflow runs (next Monday, or manually), it'll reuse the account key from the secret.

## Verify the safety net

After the first install, test the expiry-check workflow:

1. Actions → **SSL expiry check** → **Run workflow** → Run.
2. It should complete with no issue created (since cert is freshly installed).
3. The daily cron will start running automatically.

## Delete this INSTALL.md once installation is done

This file is just for the one-time setup. After everything is committed and tested, you can `rm INSTALL.md` and commit that.
