# SmakMail examples

Minimal examples for working with SmakMail receive-only mailboxes.

SmakMail provides persistent receive-only mailboxes for incoming messages, registrations, verification codes and automation. Purchased mailboxes can be accessed through Webmail, IMAP, POP3 and the SmakMail HTTP API.

## Protocols

- IMAP: `imap.smakmail.com`, port `993`, SSL/TLS
- POP3: `pop3.smakmail.com`, port `995`, SSL/TLS
- Login: full mailbox email address
- Password: mailbox password from the issued order

SmakMail mailboxes are receive-only. These examples do not configure SMTP or outbound sending.

Compatibility with any specific third-party service is not guaranteed.

## Examples

- `examples/imap_read.py` — list recent message headers over IMAP without marking messages as read
- `examples/pop3_list.py` — list messages over POP3 without deleting them
- `examples/tls_check.sh` — verify TLS connectivity to IMAP and POP3
- `.env.example` — environment variable names used by the scripts

## HTTP API

The HTTP API is also available for mailbox purchase and inbound-email automation. API routes and authentication details should be taken from the current SmakMail documentation rather than duplicated here, so examples do not drift from the live contract.

Current documentation:

- https://smakmail.com/en/docs/api
- https://smakmail.com/en/docs/imap
- https://smakmail.com/en/docs/pop3
- https://smakmail.com/en/email-api

Product overview:

- https://smakmail.com/en/buy-email-accounts
- https://smakmail.com/en/smakmail-mailboxes

## Security

Do not commit real mailbox credentials. Use environment variables or a local `.env` file excluded from version control.

## About SmakMail

https://smakmail.com
