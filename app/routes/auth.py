from flask import Blueprint, render_template, request, flash, session, redirect, url_for
import bcrypt, random, time, re
from email_validator import validate_email, EmailNotValidError
from app.models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")
        agree = request.form.get("agree_to_terms", "")

        # 1. Base Input Validation Checks
        if not fullname or not gmail or not password:
            flash("Please fill in all fields.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)
        
        if len(fullname) < 3 or len(fullname) > 30:
            flash("Name must be between 3 and 30 characters long.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)
        
        if len(password) < 6 or len(password) > 30:
            flash("Password must be between 6 and 30 characters long.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)
            
        try:
            email_info = validate_email(gmail, check_deliverability=False)
            gmail = email_info.normalized
            if not gmail.endswith('@gmail.com'):
                flash("Please use a valid @gmail.com address.")
                return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)
        except EmailNotValidError:
            flash("Invalid email address format.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)
        
        if not agree:
            flash("You must agree to the Terms and Privacy Policy to continue.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)

        # 2. Prevent Email Collisions
        if User.query.filter_by(email=gmail).first():
            flash("This email is already registered. Try another.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)

        # 3. Clean and Extract Base Handle Username Suffix Core
        email_prefix = gmail.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9]', '', email_prefix)

        if not base_username:
            base_username = "user"

        # 🛡️ 4. Reserved System Handle Check & Collision Auto-Resolver
        reserved_usernames = [
            "aadarshaaryan", 
            "admin", 
            "administrator", 
            "root", 
            "afflux", 
            "system", 
            "moderator"
        ]

        if base_username in reserved_usernames:
            # Force seed iteration immediately to fully preserve core keywords
            username = f"{base_username}1"
            counter = 2
        else:
            username = base_username
            counter = 1

        # Direct Query Condition Loop ensures perfect uniqueness
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        # 5. Securely hash password BEFORE putting it into temporary session data
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # 6. Store data in session temporarily for multi-step OTP tracking
        session['fullname'] = fullname
        session['username'] = username
        session['gmail'] = gmail
        session['hashed_password'] = hashed_password
        
        # --- LOCAL TESTING DEFAULT (Change when configuring production SMTP services) ---
        session['otp'] = "111111"
        session['otp_expires'] = time.time() + 600 # Valid for 10 minutes

        flash(f"We have sent a 6-digit verification code to {session['gmail']}.")
        session.modified = True
        return redirect(url_for("auth.verify_otp"))

    # Default fallback values for clean standard GET requests
    return render_template("auth/signup.html", fullname="", gmail="", agree="")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if 'gmail' not in session or 'otp' not in session:
        flash("Session expired or invalid access track. Please register again.")
        return redirect(url_for("auth.signup"))

    if request.method == "POST":
        user_otp_input = request.form.get("otp", "").strip()
        
        if time.time() > session.get('otp_expires', 0):
            flash("Your verification code has expired. Please sign up again.")
            return redirect(url_for("auth.signup"))

        if str(user_otp_input) == str(session.get('otp')):
            # 1. Instantiate new user record mapping directly to database schema
            new_user = User(
                name=session['fullname'],
                username=session['username'],
                email=session['gmail'],
                password_hash=session['hashed_password']
            )
            
            # 💡 Hook up default admin logic if registering your primary handle
            if new_user.username == "aadarshaaryan":
                new_user.is_admin = True

            db.session.add(new_user)
            db.session.commit()
            
            # 2. AUTOMATIC DIRECT SIGN-IN: Populate session storage variables
            session["user_id"] = new_user.id
            session["username"] = new_user.username
            session["is_admin"] = new_user.is_admin 
            
            # 3. Clean out temporary registration cache variables safely
            for key in ['fullname', 'gmail', 'hashed_password', 'otp', 'otp_expires']:
                session.pop(key, None)
            
            flash(f"Account verified successfully! Welcome, {new_user.name or new_user.username}!")
            return redirect(url_for("profile.profile", username=new_user.username))
        else:
            flash("Invalid OTP code. Please try again.")
            return render_template("auth/otp_page.html")
            
    return render_template("auth/otp_page.html")


@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if session.get("user_id") and session.get("username"):
        return redirect(url_for("profile.profile", username=session["username"]))

    if request.method == "POST":
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")

        if not gmail or not password:
            flash("Please enter both your email and password.")
            return redirect(url_for("auth.signin"))
        

        user = User.query.filter_by(email=gmail).first()

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            flash("Invalid email or password.")
            return redirect(url_for("auth.signin"))

        session["user_id"] = user.id
        session["username"] = user.username
        session["is_admin"] = user.is_admin  

        flash(f"Welcome back, {user.name or user.username}!")
        return redirect(url_for("profile.profile", username=user.username))
        
    return render_template("auth/signin.html")


@auth_bp.route("/signout")
def signout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("is_admin", None)  
    
    flash("You have been logged out successfully.")
    return redirect(url_for("auth.signin"))