from flask import Blueprint, render_template, redirect, flash, url_for, jsonify
import sqlite3
from app.services.email_service import send_email

main_bp = Blueprint("main", __name__)
DB_NAME = "database.db"

@main_bp.route('/')
def home():
    return render_template('main/index.html')

@main_bp.route('/blog')
def blog():
    return render_template('navs/blog.html')

@main_bp.route('/contacts')
def contacts():
    return render_template('navs/contacts.html')

@main_bp.route('/portfolio')
def portfolio():
    flash("I'm currently refining my portfolio to showcase my best work. It'll be available soon.")
    return redirect(url_for('main.home'))

@main_bp.route('/hackathons')
def hackathons():
    return render_template('navs/hackathons.html')

@main_bp.route("/users")
def show_users():
    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM users")
        rows = cursor.fetchall()
    return render_template("main/users.html", users=rows)


@main_bp.route("/test-email")
def test_email():
    send_email(
        "uttamkumar96442@gmail.com",
        "aaditya harami hai",
        "aaditya harami hai."
    )
    return "Email sent! Aadarsh 🥳"

@main_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200