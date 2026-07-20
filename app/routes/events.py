# app/routes/events.py
from flask import Blueprint, render_template
from app.models import Event

events_bp = Blueprint("events", __name__, url_prefix="/events")

@events_bp.route("/")
def list_events():
    # Fetch all events once to avoid multiple DB hits
    all_events = Event.query.order_by(Event.registration_deadline.asc()).all()
    
    # Use the existing @property .status logic from models.py
    # This is cleaner and ensures consistency across your app
    open_events = []
    upcoming_events = []
    closed_events = []

    for event in all_events:
        status = event.status  # Uses the property defined in models.py
        if status == "open":
            open_events.append(event)
        elif status == "upcoming":
            upcoming_events.append(event)
        else:
            closed_events.append(event)

    return render_template(
        "events/events.html",
        open_events=open_events,
        upcoming_events=upcoming_events,
        closed_events=closed_events
    )