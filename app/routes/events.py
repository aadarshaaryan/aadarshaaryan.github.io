# app/routes/events.py
from flask import Blueprint, render_template
from app.models import Event

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def list_events():
    # Fetch all rows from the database ordered by closest deadline
    all_events = Event.query.order_by(Event.registration_deadline.asc()).all()
    
    # Sort them using the updated model status criteria
    open_events = [e for e in all_events if e.status == "open"]
    upcoming_events = [e for e in all_events if e.status == "upcoming"]
    closed_events = [e for e in all_events if e.status == "closed"]
    
    return render_template(
        'events/events.html', 
        open_events=open_events, 
        upcoming_events=upcoming_events, 
        closed_events=closed_events
    )