import os

from smakmail_client import SmakMailClient


client = SmakMailClient(os.environ["SMAKMAIL_API_KEY"])

email = os.environ["SMAKMAIL_EMAIL"]
mailbox_password = os.environ.get("SMAKMAIL_MAILBOX_PASSWORD")

messages = client.mailbox_messages(
    email,
    mailbox_password=mailbox_password,
)
print(messages)

latest_code = client.mailbox_latest_code(
    email,
    mailbox_password=mailbox_password,
)
print(latest_code)
