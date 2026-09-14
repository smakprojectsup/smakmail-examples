#!/usr/bin/env python3
import os
import poplib

HOST = "pop3.smakmail.com"
PORT = 995

username = os.environ["SMAKMAIL_EMAIL"]
password = os.environ["SMAKMAIL_PASSWORD"]

client = poplib.POP3_SSL(HOST, PORT, timeout=20)
try:
    client.user(username)
    client.pass_(password)

    count, mailbox_size = client.stat()
    print(f"Messages: {count}")
    print(f"Mailbox size: {mailbox_size} bytes")

    _, lines, _ = client.list()
    for line in lines[-10:]:
        print(line.decode())
finally:
    client.quit()
