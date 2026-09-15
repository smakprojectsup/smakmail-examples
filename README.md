# SmakMail persistent mailbox API, IMAP and POP3 examples

Examples, OpenAPI and a small Python client for SmakMail persistent receive-only mailboxes.

SmakMail provides managed mailboxes for registrations, verification codes and inbound-email automation. Mailboxes are issued with login/password credentials and can be accessed through Webmail, IMAP, POP3 and the SmakMail HTTP API.

SmakMail is not an outbound SMTP service and does not sell pre-existing Gmail or Outlook accounts. The core product is persistent receive-only mailboxes on SmakMail-managed domain pools. Compatibility with any specific third-party service is not guaranteed.

## Install the Python client

```bash
python -m pip install smakmail-client
```

PyPI:

- https://pypi.org/project/smakmail-client/

Source install:

```bash
python -m pip install git+https://github.com/smakprojectsup/smakmail-examples.git
```

## Protocols

- IMAP: `imap.smakmail.com`, port `993`, SSL/TLS
- POP3: `pop3.smakmail.com`, port `995`, SSL/TLS
- Login: full mailbox email address
- Password: mailbox password from the issued order
- HTTP API base URL: `https://api.smakmail.com/api/v1`

SmakMail mailboxes are receive-only. These examples do not configure SMTP or outbound sending.

## Examples

- `examples/imap_read.py` — list recent message headers over IMAP without marking messages as read
- `examples/pop3_list.py` — list messages over POP3 without deleting them
- `examples/tls_check.sh` — verify TLS connectivity to IMAP and POP3
- `examples/api_read.py` — read mailbox messages and the latest extracted verification code through the HTTP API
- `.env.example` — environment variable names used by the scripts

## Python API client

Example:

```python
import os

from smakmail_client import SmakMailClient

client = SmakMailClient(os.environ["SMAKMAIL_API_KEY"])

messages = client.mailbox_messages(
    os.environ["SMAKMAIL_EMAIL"],
    mailbox_password=os.environ.get("SMAKMAIL_MAILBOX_PASSWORD"),
)
print(messages)

latest_code = client.mailbox_latest_code(
    os.environ["SMAKMAIL_EMAIL"],
    mailbox_password=os.environ.get("SMAKMAIL_MAILBOX_PASSWORD"),
)
print(latest_code)
```

The API key is sent as `Authorization: Bearer <API_KEY>` and identifies the API caller. `X-Mailbox-Password` is sent when `mailbox_password` is provided. It is used for credential-authorized mailbox reads where required. Reading a mailbox owned by another SmakMail account with mailbox credentials is a Developer API capability and does not grant access to that owner's account, billing, API keys or mailbox management.

The client intentionally returns the live API JSON as-is instead of freezing response schemas in this repository.

## OpenAPI

`openapi.yaml` provides a partial OpenAPI 3.1 description of the verified public read surface used by the Python client:

- `GET /me`
- `GET /mailbox/messages?email=...`
- `GET /mailbox/latest-code?email=...`

The spec deliberately leaves response bodies open-ended instead of inventing undocumented fields.

## Documentation

API:

- https://smakmail.com/en/docs/api
- https://smakmail.com/en/email-api

IMAP and POP3:

- https://smakmail.com/en/docs/imap
- https://smakmail.com/en/docs/pop3

Product overview:

- https://smakmail.com/en/buy-email-accounts
- https://smakmail.com/en/smakmail-mailboxes

## Security

Do not commit real API keys or mailbox credentials. Use environment variables or a local `.env` file excluded from version control.

## About SmakMail

https://smakmail.com
