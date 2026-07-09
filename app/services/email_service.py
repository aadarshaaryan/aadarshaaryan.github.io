from flask_mail import Message
from app import mail

def send_email(to, subject, body):
    """
    Send an HTML formatted email.
    """
    msg = Message(
        subject=subject,
        recipients=[to],
        html=body
    )
    mail.send(msg)