# from flask_mail import Message
# from app import mail
# from threading import Thread
# from flask import current_app

# def send_async_email(app, msg):
#     # Flask-Mail requires an active application context to access configuration fields safely
#     with app.app_context():
#         mail.send(msg)

# def send_email(to, subject, body):
#     """
#     Send an HTML formatted email asynchronously using background threading.
#     """
#     # Grab a reference to the active production application instance
#     app = current_app._get_current_object()
    
#     msg = Message(
#         subject=subject,
#         recipients=[to],
#         html=body
#     )
    
#     # Spin up an isolated background thread to handle the network traffic socket handshake
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()
#     return thr

import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(to, subject, body):
    params = {
        "from": "Afflux <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": body,
    }

    return resend.Emails.send(params)