from flask import Blueprint, render_template, request, flash, session, redirect, url_for
import sqlite3
import bcrypt

auth_bp = Blueprint("auth", __name__)
DB_NAME = "database.db"

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in both fields.")
            return redirect(url_for("auth.signup"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return redirect(url_for("auth.signup"))

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            with sqlite3.connect(DB_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)", 
                    (username, hashed_password)
                )
                connection.commit()
                
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                user_id = cursor.fetchone()[0]

            
            session["user_id"] = user_id
            session["username"] = username

            flash(f"Signup successful! Welcome, {username}.")
            return redirect(url_for("profile.profile"))

        except sqlite3.IntegrityError:
            flash("Username already exists. Try another.")
            return redirect(url_for("auth.signup"))

    flash("Sign up")
    return render_template("auth/signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash(f"Login successful! {session['username']}")
            return redirect(url_for("profile.profile"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))
        
    flash("Sign in")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))