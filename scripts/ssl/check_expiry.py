#!/usr/bin/env python3
"""
Read live SSL certs for each domain, write a summary to GITHUB_OUTPUT,
and exit 0 (always — used by a GitHub Actions step that decides what to do
based on the output values).

Outputs (written to $GITHUB_OUTPUT):
    min_days       integer, min days until expiry across all domains
    needs_renewal  "true" | "false"
    summary        markdown table with per-domain rows
"""
import datetime
import os
import socket
import ssl
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend

DOMAINS = ["sdts.org", "www.sdts.org", "bts.sdts.org", "www.bts.sdts.org"]
THRESHOLD_DAYS = 21


def fetch_expiry(host, port=443):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                der = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(der, default_backend())
                return cert.not_valid_after_utc.replace(tzinfo=None)
    except Exception as e:
        return e


now = datetime.datetime.utcnow()
rows = []
days_list = []
for d in DOMAINS:
    exp = fetch_expiry(d)
    if isinstance(exp, datetime.datetime):
        days = (exp - now).days
        days_list.append(days)
        rows.append(f"| {d} | {exp.date()} | {days} |")
    else:
        rows.append(f"| {d} | ERROR | {exp} |")

table = "| Domain | Expires | Days remaining |\n|---|---|---|\n" + "\n".join(rows)
min_days = min(days_list) if days_list else -1
needs_renewal = "true" if (min_days < 0 or min_days <= THRESHOLD_DAYS) else "false"

# Print for the workflow log
print(table)
print(f"\nmin_days={min_days}  needs_renewal={needs_renewal}")

# Write to $GITHUB_OUTPUT
gh_out = os.environ.get("GITHUB_OUTPUT")
if gh_out:
    with open(gh_out, "a") as f:
        f.write(f"min_days={min_days}\n")
        f.write(f"needs_renewal={needs_renewal}\n")
        # multi-line summary uses heredoc syntax
        f.write("summary<<EOF\n")
        f.write(table)
        f.write("\nEOF\n")
