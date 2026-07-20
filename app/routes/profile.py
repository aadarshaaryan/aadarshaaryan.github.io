from flask import Blueprint, render_template, session, abort, redirect, url_for, flash, request
from app.models import User, db
from app.models import EventResult
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from validators import url as is_valid_url
import cloudinary.uploader
import cloudinary
from app.routes.achievements_engine import check_and_sync_achievements

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/u/<username>")
def profile(username):
    # Fetch user case-insensitively
    user_record = User.query.filter(User.username.ilike(username)).first()
    
    if not user_record:
        abort(404)

    # Core metric counters
    events_count = EventResult.query.filter_by(user_id=user_record.id).count()
    certs_count = EventResult.query.filter(
        EventResult.user_id == user_record.id,
        EventResult.certificate_code.isnot(None) 
    ).count()

    # Ownership verification (True only if logged in AND viewing own page)
    is_owner = current_user.is_authenticated and (current_user.id == user_record.id)

    # Flag to signal the template layer to check browser localStorage
    check_guest_ownership = not current_user.is_authenticated

    # Leaderboard / Top 3 evaluation
    all_users = User.query.all()
    all_users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    top_three = all_users[:3]
    top_three_ids = [u.id for u in top_three]

    # Evaluate/Sync achievements only if the true owner is logged in and looking
    if is_owner:
        check_and_sync_achievements(user_record)

    # Build the required matrix dictionary context structure using your helper engine
    from app.routes.achievements_engine import get_achievements_view_matrix
    badge_categories = get_achievements_view_matrix(user_record)

    # Dynamically count unlocked achievements across all matrix categories
    unlocked_badges_count = sum(
        1 for badges in badge_categories.values() 
        for badge in badges 
        if (isinstance(badge, dict) and badge.get('unlocked')) or (not isinstance(badge, dict) and getattr(badge, 'unlocked', False))
    )

    return render_template(
        "profile/profile.html", 
        target_user=user_record,
        is_owner=is_owner,
        check_guest_ownership=check_guest_ownership,  # Passed context safely here!
        events_count=events_count,
        certs_count=certs_count,
        top_three_ids=top_three_ids,
        badge_categories=badge_categories,
        unlocked_count=unlocked_badges_count
    )


@profile_bp.route("/users")
def users():
    # Fetch ALL users
    all_users = User.query.all()
    
    # Sort them by level and XP, same as your leaderboard logic
    all_users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    
    # Pass the sorted list to the template
    return render_template("profile/users.html", users=all_users)

@profile_bp.route("/update-participation/<int:result_id>", methods=['POST'])
@login_required # Ensures the user is logged in via Flask-Login
def update_participation(result_id):
    result = EventResult.query.get_or_404(result_id)
    
    # Check if the authenticated user owns this result
    if current_user.id != result.user_id:
        flash("Unauthorized.")
        return redirect(url_for("profile.profile", username=current_user.username))
    
    new_name = request.form.get("participant_name")
    if new_name:
        result.participant_name = new_name
        db.session.commit()
        flash("Display name updated for this event.")
    
    return redirect(url_for("profile.profile", username=current_user.username))


@profile_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # 1. VALIDATION PHASE
        form_data = request.form.to_dict()
        social_fields = ['github', 'linkedin', 'website', 'instagram', 'youtube']
        
        for field in social_fields:
            val = request.form.get(field)
            if val and not is_valid_url(val):
                flash(f"Invalid URL format for {field.capitalize()}.", "error")
                return render_template('profile/edit_profile.html', target_user=current_user, form_data=form_data)
        
        # Check password match early
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password and new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('profile/edit_profile.html', target_user=current_user, form_data=form_data)

        # 2. IMAGE UPLOAD PROCESSING PIPELINE
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                try:
                    # Uploads file directly using the user's username parameter reference
                    upload_result = cloudinary.uploader.upload(
                        file,
                        folder="afflux_profiles",
                        public_id=f"user_{current_user.username}",
                        overwrite=True,
                        resource_type="image"
                    )
                    # Bind the resulting secure asset address directly to the user object record column
                    current_user.profile_pic = upload_result.get("secure_url")
                except Exception as e:
                    print(f"Cloudinary Production Upload Error: {e}")
                    flash("Failed to process and upload asset to host storage.", "error")
                    return render_template('profile/edit_profile.html', target_user=current_user, form_data=form_data)

        # 3. UPDATE PHASE (Only reached if validation passes)
        current_user.name = request.form.get('name')
        current_user.bio = request.form.get('bio')
        
        for field in social_fields:
            setattr(current_user, field, request.form.get(field))

        if new_password:
            current_user.password_hash = generate_password_hash(new_password)

        # 4. XP REWARD LOGIC
        if all([current_user.name, current_user.bio, current_user.github]) and not getattr(current_user, 'xp_awarded', False):
            current_user.xp += 500
            current_user.xp_awarded = True # Set flag to true preventing infinite farm loop resets
            flash("Profile complete! You earned 500 XP.", "success")

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('profile.profile', username=current_user.username))

    return render_template('profile/edit_profile.html', target_user=current_user)

@profile_bp.route('/leaderboard')
def leaderboard():
    all_users = User.query.all()
    all_users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    top_20_users = all_users[:20]
    return render_template("profile/leaderboard.html", users=top_20_users)