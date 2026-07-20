# app/__init__.py
from flask import Flask, render_template, session, request
from dotenv import load_dotenv
from app.extensions import db, migrate
import os
from flask_login import LoginManager
from app.models import User



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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')

    # app/__init__.py
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin' # Use the name of your signin route

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.hackathons import hackathons_bp
    from app.routes.events import events_bp
    from app.routes.admin import admin_bp
    from app.routes.certificates import certificates_bp
    from app.routes.achievements import achievements_bp
    from app.routes.achievements_engine import achievements_engine_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(hackathons_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(achievements_engine_bp)

    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        # This queries the database for the user with the given ID
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def page_not_found(e):
        for key in ['fullname', 'gmail', 'hashed_password', 'otp', 'otp_expires']:
            session.pop(key, None)
        return render_template("extra/404.html"), 404
        
    return app