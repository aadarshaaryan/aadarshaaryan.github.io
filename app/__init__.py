from flask import Flask, jsonify
import os
from app.models import init_db

def create_app():
    app = Flask(__name__)
    
    # Configuration Management
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "jgfjiosfjksdfjosd_fallback_key")
    
    # Initialize SQLite structural tables within application context
    with app.app_context():
        init_db()

    # Register separated blueprint routing blocks
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp  # Matches the variable name now

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    # Standard global fallback error page
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    return app