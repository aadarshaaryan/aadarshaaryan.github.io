from flask_mail import Message
from app import mail


def send_email(to, subject, body):
    """
    Send a plain text email.
    """
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body
    )
    mail.send(msg)