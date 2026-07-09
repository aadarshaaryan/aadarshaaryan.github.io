import os
import base64

from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_email(to, subject, body):
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    # Get fresh access token
    creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body, "html")
    message["to"] = to
    message["from"] = f"Afflux <{os.getenv('GMAIL_SENDER')}>"
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()