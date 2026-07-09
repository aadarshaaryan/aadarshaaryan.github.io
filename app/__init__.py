from flask import Flask, render_template
from dotenv import load_dotenv
import os

from app.extensions import db, mail

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY",
        "4a7b2e91f3c8d0e5b7a692341d6f5e8c7b8a1234567890abcdef1234567890ab"
    )

    # PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # TEMPORARY: show SQL queries in terminal
    app.config["SQLALCHEMY_ECHO"] = True

    # Mail
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
    app.config["MAIL_USE_TLS"] = (
        os.getenv("MAIL_USE_TLS") == "True"
    )
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = f"Afflux <{os.getenv('MAIL_USERNAME')}>"
    app.config["MAIL_TIMEOUT"] = 10

    print("SERVER:", app.config["MAIL_SERVER"])
    print("PORT:", app.config["MAIL_PORT"])
    print("TLS:", app.config["MAIL_USE_TLS"])
    print("USER:", app.config["MAIL_USERNAME"])

    db.init_app(app)
    mail.init_app(app)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.hackathons import hackathons_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(hackathons_bp)

    @app.route("/smtp-test")
    def smtp_test():
        import smtplib

        try:
            s = smtplib.SMTP(
                "smtp.gmail.com",
                587,
                timeout=10
            )
            s.quit()
            return "Connected!"
        except Exception as e:
            return str(e)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("extra/404.html"), 404

    return app