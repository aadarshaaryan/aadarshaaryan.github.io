from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)
DB_NAME = "database.db"

@main_bp.route('/')
def home():
    return render_template('main/index.html')

@main_bp.route('/contacts')
def contacts():
    return render_template('navs/contacts.html')

@main_bp.route("/privacy-policy")
def privacy_policy():
    """Renders the enhanced platform privacy terms."""
    return render_template("legal/privacy.html")

@main_bp.route("/terms-of-service")
def terms_of_service():
    """Renders the updated platform usage guidelines and leaderboard rules."""
    return render_template("legal/terms.html")