# app/routes/achievements_engine.py

import json
import re
from flask import Blueprint, flash
from sqlalchemy.orm.attributes import flag_modified
from app.models import db, EventResult
from app.routes.achievements import ACHIEVEMENTS
from datetime import datetime

achievements_engine_bp = Blueprint("achievements_engine", __name__)

def radical_parse_achievements(raw_data):
    """
    Safely intercepts and decodes raw data payloads, fully neutralizing 
    double-serialized strings and database driver escape anomalies.
    """
    if not raw_data:
        return {}
    if isinstance(raw_data, dict):
        return raw_data

    if isinstance(raw_data, str):
        # Strip outer white space or accidental duplicate literal wrappers
        cleaned = raw_data.strip().strip('"').strip("'")
        cleaned = cleaned.replace('""', '"')
        
        try:
            parsed = json.loads(cleaned)
            # If standard single-pass parsing gives us a dictionary, use it
            if isinstance(parsed, dict):
                return parsed
            
            # DOUBLE-SERIALIZATION DETECTED: If the output is still a string, process it again
            if isinstance(parsed, str):
                second_pass = json.loads(parsed)
                if isinstance(second_pass, dict):
                    return second_pass
        except Exception:
            # Emergency Regex fallback parsing block if JSON sub-structures choke
            extracted = {}
            pattern = r'"([^"]+)":\s*"([^"]+)"'
            matches = re.findall(pattern, cleaned)
            for k, v in matches:
                extracted[k] = v
            return extracted

    try:
        return {aid: datetime.utcnow().isoformat() for aid in raw_data}
    except Exception:
        return {}


def check_and_sync_achievements(user):
    """Evaluates user milestones and writes newly unlocked badges to database storage."""
    if not user:
        return False

    user.achievements = radical_parse_achievements(user.achievements)

    events_joined = EventResult.query.filter_by(user_id=user.id).count()
    certs_count = EventResult.query.filter(
        EventResult.user_id == user.id, 
        EventResult.certificate_code.isnot(None)
    ).count()
    
    first_places_count = EventResult.query.filter(EventResult.user_id == user.id, EventResult.position == 1).count()
    second_places_count = EventResult.query.filter(EventResult.user_id == user.id, EventResult.position == 2).count()
    third_places_count = EventResult.query.filter(EventResult.user_id == user.id, EventResult.position == 3).count()

    ctx = {
        "events_joined": events_joined,
        "certs_count": certs_count,
        "current_hour": datetime.utcnow().hour,
        "wins_count": first_places_count,
        "first_places": first_places_count,
        "second_places": second_places_count,
        "third_places": third_places_count,
        "days_away": getattr(user, 'last_login_delta_days', 0)
    }
    
    mutated = False
    current_time_str = datetime.utcnow().isoformat()
    
    for category, badge_list in ACHIEVEMENTS.items():
        for badge in badge_list:
            b_id = badge["id"]
            if b_id in user.achievements:
                continue
                
            if badge["condition"](user, ctx):
                user.achievements[b_id] = current_time_str
                mutated = True
                flash(f"🏆 Achievement Unlocked: {badge['name']} — {badge['description']}", "success")

    if mutated:
        flag_modified(user, "achievements")
        db.session.commit()
        
    return mutated


def get_achievements_view_matrix(user):
    """Assembles the final display matrix. Read-only and safe for public routing queries."""
    user_badges = radical_parse_achievements(user.achievements) if user else {}
    view_matrix = {}
    
    for category, badge_list in ACHIEVEMENTS.items():
        view_matrix[category] = []
        for badge in badge_list:
            b_id = badge["id"]
            is_unlocked = b_id in user_badges
            
            view_matrix[category].append({
                "id": b_id,
                "name": badge["name"],
                "description": badge["description"],
                "unlocked": is_unlocked,
                "unlocked_at": user_badges.get(b_id) if is_unlocked else None
            })
            
    return view_matrix