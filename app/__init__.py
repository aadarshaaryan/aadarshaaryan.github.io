# app/__init__.py
from flask import Flask, render_template, session
from dotenv import load_dotenv
from app.extensions import db, migrate  # 1. Import migrate here
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY",
        "4a7b2e91f3c8d0e5b7a692341d6f5e8c7b8a1234567890abcdef1234567890ab"
    )

    # PostgreSQL config
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)  # 2. Add this right here to link migrations!

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.hackathons import hackathons_bp
    from app.routes.events import events_bp
    from app.routes.admin import admin_bp  # 3. Add Admin blueprint

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(hackathons_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)      # 4. Register Admin blueprint

    @app.errorhandler(404)
    def page_not_found(e):
        for key in ['fullname', 'gmail', 'hashed_password', 'otp', 'otp_expires']:
            session.pop(key, None)
        return render_template("extra/404.html"), 404
        
    return app