from flask import Blueprint, render_template, session, abort, redirect, url_for, flash
from app.models import User, db

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/u/<username>")
def profile(username):
    # Step 1: Find the target user being viewed (case-insensitive query)
    user_record = User.query.filter(User.username.ilike(username)).first()
    
    # Handle missing account vectors cleanly
    if not user_record:
        # Edge Case Shield: If the visitor thinks they are logged in as this person,
        # but the database row is empty, wipe the local cookies.
        if session.get("username") and session.get("username").lower() == username.lower():
            session.clear()
            flash("Your profile node could not be verified by the core database.")
            return redirect(url_for("auth.signin"))
            
        abort(404)

    # Step 2: Determine if the active visitor is the true profile owner
    logged_in_id = session.get("user_id")
    is_owner = (logged_in_id is not None) and (logged_in_id == user_record.id)

    # Step 3: Render the profile layout explicitly named to prevent global collisions
    return render_template(
        "profile/profile.html", 
        target_user=user_record,  # Renamed to target_user to protect navbar scoping!
        is_owner=is_owner
    )


@profile_bp.route("/users")
def users():
    all_users = User.query.all()
    return render_template("profile/users.html", users=all_users)