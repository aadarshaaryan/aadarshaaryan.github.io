from flask import Flask, render_template
from flask_mail import Mail
from dotenv import load_dotenv
import os

from app.models import init_db

load_dotenv()

mail = Mail()


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get(
        "FLASK_SECRET_KEY",
        "jgfjiosfjksdfjosd_fallback_key"
    )

    # Mail Configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = (
    "Afflux",
    os.getenv("MAIL_USERNAME")
)

    # Initialize Flask-Mail
    mail.init_app(app)

    with app.app_context():
        init_db()

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.hackathons import hackathons_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(hackathons_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("extra/404.html"), 404

    return app