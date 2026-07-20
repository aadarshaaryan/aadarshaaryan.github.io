from flask import Blueprint, render_template, request, flash, session, redirect, url_for
import bcrypt, time, re, random
from email_validator import validate_email, EmailNotValidError
from app.models import db, User, EventResult
from flask_login import login_user, current_user
import time
from app.routes.achievements_engine import check_and_sync_achievements
from app.services.email_service import send_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")
        agree = request.form.get("agree_to_terms", "")

        if not fullname or not gmail or not password:
            flash("Please fill in all fields.")
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

        if User.query.filter_by(email=gmail).first():
            flash("This email is already registered. Try another.")
            return render_template("auth/signup.html", fullname=fullname, gmail=gmail, agree=agree)

        email_prefix = gmail.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9]', '', email_prefix) or "user"

        reserved = ["aadarshaaryan", "admin", "administrator", "root", "afflux", "system", "moderator"]
        username = f"{base_username}1" if base_username in reserved else base_username
        counter = 2 if base_username in reserved else 1
        
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        otp = str(random.randint(100000, 999999))

        session.update({
            'fullname': fullname,
            'username': username,
            'gmail': gmail,
            'hashed_password': hashed_password,
            'otp': otp,
            'otp_expires': int(time.time()) + 600
        })

        otp_body = render_template("auth/otp_body.html", otp=otp)
        send_email(
            session['gmail'],
            f"{otp} is your Afflux verification code",
            otp_body
        )

        flash(f"Verification code sent to {gmail}.")
        session.modified = True
        return redirect(url_for("auth.verify_otp"))
    
    return render_template("auth/signup.html", fullname="", gmail="", agree="")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if 'gmail' not in session or 'otp' not in session:
        return redirect(url_for("auth.signup"))

    if request.method == "POST":
        user_otp_input = request.form.get("otp", "").strip()
        
        # Check expiration
        if time.time() > session.get('otp_expires', 0):
            flash("Code expired.")
            return redirect(url_for("auth.signup"))

        # Verify OTP value matching
        if str(user_otp_input) == str(session.get('otp')):
            # 1. Create and configure the User instance
            new_user = User(
                name=session['fullname'],
                username=session['username'],
                email=session['gmail'],
                password_hash=session['hashed_password']
            )
            
            if new_user.username == "aadarshaaryan":
                new_user.is_admin = True

            db.session.add(new_user)
            db.session.commit()
            
            # 2. MAGIC LINK: Claim anonymous event submissions
            pending_submissions = EventResult.query.filter_by(participant_email=new_user.email, user_id=None).all()
            for sub in pending_submissions:
                sub.user_id = new_user.id
            db.session.commit()
            
            # 3. Direct Sign-in via Flask-Login (Fixes is_owner identity context)
            login_user(new_user)
            
            # 4. Clean up temporary registration session variables
            for key in ['fullname', 'gmail', 'hashed_password', 'otp', 'otp_expires', 'username']:
                session.pop(key, None)

            check_and_sync_achievements(new_user)
            
            flash(f"Welcome, {new_user.name or new_user.username}!")
            return redirect(url_for("profile.profile", username=new_user.username))
        else:
            flash("Invalid OTP.")
            return render_template("auth/otp_page.html")
            
    return render_template("auth/otp_page.html")

@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    # Check if already authenticated via Flask-Login
    if current_user.is_authenticated:
        return redirect(url_for("profile.profile", username=current_user.username))

    if request.method == "POST":
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=gmail).first()

        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            # Claim anonymous submissions
            pending_subs = EventResult.query.filter_by(participant_email=user.email, user_id=None).all()
            for sub in pending_subs:
                sub.user_id = user.id
            db.session.commit()

            # Flask-Login session management
            login_user(user)

            # Current time in seconds
            now_seconds = int(time.time())

            # Check if last_signed_in exists
            if current_user.last_signed_in :
                # If at least 24 hours (86400 seconds) have passed
                if now_seconds - current_user.last_signed_in >= 86400:
                    current_user.xp += 50
            else:
                # First sign-in case
                current_user.signed_in = 1

            # Update last_signed_in to now
            current_user.last_signed_in = now_seconds

            # Check for streak bonuses
            if user.signed_in % 30 == 0:
                user.xp += 2000
                flash("Monthly Legend! +2000 XP for your 30th login.", "success")
            elif user.signed_in % 7 == 0:
                user.xp += 500
                flash("Weekly Streak! +500 XP for your 7th login.", "success")
            else:
                flash(f"Welcome back! Login streak: {user.signed_in}.", "info")

            db.session.commit()

            check_and_sync_achievements(current_user)

            flash(f"Login successfull {current_user.name}")
            return redirect(url_for("profile.profile", username=user.username))
        
        flash("Invalid email or password.")
    return render_template("auth/signin.html")

@auth_bp.route("/signout")
def signout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("auth.signin"))