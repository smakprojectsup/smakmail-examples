#!/usr/bin/env bash
set -euo pipefail

echo "=== IMAP 993 SSL/TLS ==="
openssl s_client -connect imap.smakmail.com:993 -servername imap.smakmail.com -brief </dev/null

echo
echo "=== POP3 995 SSL/TLS ==="
openssl s_client -connect pop3.smakmail.com:995 -servername pop3.smakmail.com -brief </dev/null
