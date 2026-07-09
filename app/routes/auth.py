from flask import Blueprint, render_template, request, flash, session, redirect, url_for
import bcrypt, random, time
from email_validator import validate_email, EmailNotValidError
from app.models import db, User
from app.services.email_service import send_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")
        agree = request.form.get("agree_to_terms", "")

        # 1. Validation Checks
        if not fullname or not gmail or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("auth.signup"))
        
        if len(fullname) < 3 or len(fullname) > 30:
            flash("Name must be between 3 and 30 characters long.")
            return redirect(url_for("auth.signup"))
        
        if len(password) < 6 or len(password) > 30:
            flash("Password must be between 6 and 30 characters long.")
            return redirect(url_for("auth.signup"))
            
        try:
            email_info = validate_email(gmail, check_deliverability=False)
            gmail = email_info.normalized
            if not gmail.endswith('@gmail.com'):
                flash("Please use a valid @gmail.com address.")
                return redirect(url_for("auth.signup"))
        except EmailNotValidError:
            flash("Invalid email address format.")
            return redirect(url_for("auth.signup"))
        
        if not agree:
            flash("You must agree to the Terms and Privacy Policy to continue.")
            return redirect(url_for("auth.signup"))

        # 2. Store temporary signup info in session
        session['fullname'] = fullname
        session['gmail'] = gmail
        session['password'] = password

        # 3. Generate OTP
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['otp_expires'] = time.time()

        # 4. Render OTP email body and send
        otp_body = render_template("auth/otp_body.html", otp=otp)
        send_email(
            session['gmail'],
            "Verify Your Email — Afflux Account Creation",
            otp_body
        )

        flash(f"We sent an OTP to {session['gmail']}")
        
        session.modified = True
        
        return redirect(url_for("auth.verify_otp"))

    return render_template("auth/signup.html")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    # 🛡️ ROUTE GUARD: Check if the user actually came from a valid registration step
    if 'gmail' not in session or 'otp' not in session:
        flash("Please fill out the signup form first.")
        return redirect(url_for("auth.signup"))

    # If it's a POST request (the user typed the code and clicked verify)
    if request.method == "POST":
        user_otp_input = request.form.get("otp")
        
        # Check for expiration
        if time.time() > session.get('otp_expires', 0) + 600: # 5 minutes expiry
            flash("Your OTP has expired. Please sign up again.")
            return redirect(url_for("auth.signup"))

        # Verify the code
        if str(user_otp_input) == str(session.get('otp')):
            # Success! Save the user to PostgreSQL database here...
            
            # Clear out the temporary signup data from session
            session.pop('otp', None)
            session.pop('password', None)
            
            flash("Account verified successfully! Please sign in.")
            return redirect(url_for("auth.signin"))
        else:
            flash("Invalid OTP code. Please try again.")
            return render_template("auth/otp_page.html")
        
    return render_template("auth/otp_page.html")


@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        gmail = request.form.get("gmail", "").strip().lower()
        password = request.form.get("password", "")

        if not gmail or not password:
            flash("Please enter both your email and password.")
            return redirect(url_for("auth.signin"))

        user = User.query.filter_by(gmail=gmail).first()

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            flash("Invalid email or password.")
            return redirect(url_for("auth.signin"))

        session["user_id"] = user.id
        session["username"] = user.fullname

        flash(f"Welcome back, {user.fullname}!")
        return redirect(url_for("profile.profile"))

    return render_template("auth/signin.html")