# app/routes/admin.py
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app.models import Event, EventResult, User
from app.extensions import db
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re
from flask_login import current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_to_admin():
    # Strict single-admin check as requested
    if not current_user.is_authenticated or current_user.username != 'aadarshaaryan': 
        flash("Unauthorized access.")
        return redirect(url_for('main.home'))

@admin_bp.route('/dashboard')
def dashboard():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/dashboard.html', events=events)

def generate_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower().strip())
    return re.sub(r'[\s_-]+', '-', slug)

@admin_bp.route('/post-event', methods=['GET', 'POST'])
def post_event():
    if request.method == 'POST':
        def parse_to_utc(field):
            value = request.form.get(field)
            if not value: return None
            return datetime.strptime(value, "%Y-%m-%dT%H:%M").replace(tzinfo=ZoneInfo("Asia/Kolkata")).astimezone(timezone.utc)

        try:
            new_event = Event(
                title=request.form.get('title'),
                slug=generate_slug(request.form.get('title')),
                short_description=request.form.get('short_description'),
                category=request.form.get('category'),
                registration_deadline=parse_to_utc('registration_deadline'),
                submission_deadline=parse_to_utc('submission_deadline'),
                registration_url=request.form.get('registration_url'),
                submission_url=request.form.get('submission_url')
            )
            db.session.add(new_event)
            db.session.commit()
            flash("Event added successfully.")
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Deployment failed: {str(e)}")
    return render_template('admin/post_event.html')

@admin_bp.route('/upload-submissions/<int:event_id>', methods=['POST'])
def upload_submissions(event_id):
    event = Event.query.get_or_404(event_id)
    file = request.files.get('file')
    
    if not file or not file.filename.endswith('.csv'):
        flash("Invalid file.")
        return redirect(url_for('admin.dashboard'))

    try:
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        
        updated_count = 0
        created_count = 0
        
        for row in reader:
            email = (row.get('Email Address') or row.get('email') or '').strip().lower()
            name = row.get('Full Name') or row.get('name')
            if not email: continue
            
            sub = EventResult.query.filter_by(event_id=event.id, participant_email=email).first()
            
            sub_data = {
                k: v for k, v in row.items() 
                if k not in ['Email Address', 'email', 'Full Name', 'name', 'team_name', 'Team Name']
            }
            
            if sub:
                sub.participant_name = name or sub.participant_name
                sub.submission_data = sub_data
                updated_count += 1
            else:
                user = User.query.filter_by(email=email).first()
                
                # --- NEW XP REWARD LOGIC ---
                if user:
                    user.xp += 100 # Participation bonus for new registrations
                
                sub = EventResult(
                    event_id=event.id,
                    participant_email=email,
                    participant_name=name or "Unknown",
                    user_id=user.id if user else None,
                    submission_data=sub_data
                )
                db.session.add(sub)
                created_count += 1
                
        db.session.commit()
        flash(f"Import complete: {created_count} new (100XP awarded each), {updated_count} updated.")
    except Exception as e:
        db.session.rollback()
        flash(f"Import error: {str(e)}")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export-submissions/<int:event_id>')
def export_submissions(event_id):
    event = Event.query.get_or_404(event_id)
    results = EventResult.query.filter_by(event_id=event_id).all()
    
    si = StringIO()
    cw = csv.writer(si)
    
    # 1. Identify all unique keys present in the JSON data across all results
    # This ensures even if some rows have extra fields, they get a column
    all_json_keys = set()
    for r in results:
        if r.submission_data:
            all_json_keys.update(r.submission_data.keys())
    
    # 2. Define the base headers + dynamic headers
    base_headers = ['ID', 'Name', 'Email', 'Team Name', 'Team Leader Email', 'Position', 'Certificate Code']
    all_headers = base_headers + sorted(list(all_json_keys))
    cw.writerow(all_headers)
    
    # 3. Write rows
    for r in results:
        # Prepare the base row
        row = [
            r.id, 
            r.participant_name, 
            r.participant_email, 
            r.team_name, 
            r.team_leader_email, 
            r.position, 
            r.certificate_code
        ]
        
        # Append values for each dynamic key (or empty string if key missing for this user)
        if r.submission_data:
            for key in sorted(list(all_json_keys)):
                row.append(r.submission_data.get(key, ''))
        else:
            # If no submission_data at all, add empty strings for all dynamic columns
            row.extend([''] * len(all_json_keys))
            
        cw.writerow(row)
    
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-disposition": f"attachment; filename=results_{event.slug}.csv"})

@admin_bp.route('/update-result/<int:result_id>', methods=['POST'])
def update_result(result_id):
    result = EventResult.query.get_or_404(result_id)
    user = User.query.filter_by(id=result.user_id).first()
    
    # Capture the old position before updating
    old_position = result.position
    new_position = request.form.get('position', type=int)
    
    # Update fields
    result.position = new_position
    result.team_name = request.form.get('team_name')
    result.team_leader_email = request.form.get('team_leader_email')
    
    # --- XP REWARD LOGIC FOR PLACEMENT ---
    if user:
        # Subtract XP from the old position
        if old_position == 1: user.xp -= 500
        elif old_position == 2: user.xp -= 300
        elif old_position == 3: user.xp -= 200
        
        # Add XP for the new position
        if new_position == 1: user.xp += 500
        elif new_position == 2: user.xp += 300
        elif new_position == 3: user.xp += 200
    
    db.session.commit()
    flash("Record and XP updated successfully.")
    return redirect(url_for('admin.manage_results', event_id=result.event_id))

@admin_bp.route('/purge-submissions/<int:event_id>', methods=['POST'])
def purge_submissions(event_id):
    EventResult.query.filter_by(event_id=event_id).delete(synchronize_session=False)
    db.session.commit()
    flash("Data wiped for this event.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/manage-results/<int:event_id>')
def manage_results(event_id):
    event = Event.query.get_or_404(event_id)
    results = EventResult.query.filter_by(event_id=event.id).order_by(EventResult.position.asc()).all()
    return render_template('admin/manage_results.html', event=event, results=results)

@admin_bp.route('/generate-certificate-code/<int:result_id>', methods=['POST'])
def generate_certificate_code(result_id):
    result = EventResult.query.get_or_404(result_id)
    if not result.certificate_code:
        # Generate format: AFX-E[EventID]-#####
        unique_id = f"{result.id:06d}"
        result.certificate_code = f"AFX-E{result.event_id}-{unique_id}"
        db.session.commit()
        flash(f"Certificate code generated: {result.certificate_code}")
    return redirect(url_for('admin.manage_results', event_id=result.event_id))