# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Event  
from app.extensions import db
from datetime import datetime, timezone

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_to_admin():
    """Security node shield: Restricts workspace entirely to your account."""
    if not session.get('username') or session.get('username') != 'aadarshaaryan': 
        flash("Access denied. Unauthorized system segment.")
        return redirect(url_for('main.home'))

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/post-event', methods=['GET', 'POST'])
def post_event():
    if request.method == 'POST':
        # 1. Capture basic text components
        title = request.form.get('title')
        short_desc = request.form.get('short_description')
        category = request.form.get('category')
        mode = request.form.get('mode')
        hosted_by = request.form.get('hosted_by') or "Afflux"
        
        reg_url = request.form.get('registration_url')
        sub_url = request.form.get('submit_url')

        # 2. Helper validation mapping structure to process dates safely into timezone-aware matrices
        def parse_utc_date(form_field):
            date_str = request.form.get(form_field)
            if not date_str:
                return None
            # Standard HTML inputs give 'YYYY-MM-DDTHH:MM' -> read it as naive local, then anchor to UTC
            naive_dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            return naive_dt.replace(tzinfo=timezone.utc)

        try:
            new_event = Event(
                title=title,
                short_description=short_desc,
                category=category,
                mode=mode,
                hosted_by=hosted_by,
                registration_start=parse_utc_date('registration_start') or datetime.now(timezone.utc),
                registration_deadline=parse_utc_date('registration_deadline'),  # 💡 Registration End & Execution Start
                event_start_date=parse_utc_date('event_start_date'),
                submission_deadline=parse_utc_date('submission_deadline'),
                registration_url=reg_url,
                submit_url=sub_url
            )
            
            db.session.add(new_event)
            db.session.commit()
            flash("System tracking sequence updated. Event is live!")
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error executing database build frame: {str(e)}")
            return redirect(url_for('admin.post_event'))

    return render_template('admin/post_event.html')