from flask import Blueprint, render_template, session, flash, redirect, url_for

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("auth.login"))  

    flash("welcome")  

    return render_template("profile/profile.html")