#!/usr/bin/env python3
import email
import imaplib
import os
from email.header import decode_header, make_header

HOST = "imap.smakmail.com"
PORT = 993

username = os.environ["SMAKMAIL_EMAIL"]
password = os.environ["SMAKMAIL_PASSWORD"]

with imaplib.IMAP4_SSL(HOST, PORT) as client:
    client.login(username, password)

    status, _ = client.select("INBOX", readonly=True)
    if status != "OK":
        raise RuntimeError("Could not select INBOX")

    status, data = client.uid("search", None, "ALL")
    if status != "OK":
        raise RuntimeError("UID SEARCH failed")

    uids = data[0].split()
    for uid in uids[-10:]:
        status, fetched = client.uid(
            "fetch",
            uid,
            "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE MESSAGE-ID)])",
        )
        if status != "OK":
            continue

        raw = next((item[1] for item in fetched if isinstance(item, tuple)), b"")
        msg = email.message_from_bytes(raw)

        subject = str(make_header(decode_header(msg.get("Subject", ""))))
        sender = str(make_header(decode_header(msg.get("From", ""))))
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")

        print(f"UID: {uid.decode()}")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Message-ID: {message_id}")
        print("-" * 60)
