# app/routes/achievements.py

from flask import Blueprint
from datetime import datetime

achievements_bp = Blueprint("achievements", __name__)

ACHIEVEMENTS = {
    "👋 Getting Started": [
        {"id": "GS_01", "name": "First Steps", "description": "Created your Afflux account.", "condition": lambda u, c: True},
        {"id": "GS_02", "name": "Identity Established", "description": "Completed your profile.", "condition": lambda u, c: all([u.name, u.bio, u.github])},
        {"id": "GS_03", "name": "New Face", "description": "Added a profile picture.", "condition": lambda u, c: bool(u.profile_pic)},
        {"id": "GS_04", "name": "Connected", "description": "Verified your email.", "condition": lambda u, c: getattr(u, 'is_verified', False)},
        {"id": "GS_05", "name": "About Me", "description": "Added a bio.", "condition": lambda u, c: bool(u.bio)}
    ],
    "🔥 Activity": [
        # FIXED: Swapped 'login_count' out for 'signed_in' to align with the auth session pipeline
        {"id": "ACT_01", "name": "Welcome Back", "description": "Logged in for the first time.", "condition": lambda u, c: getattr(u, 'signed_in', 0) >= 1},
        {"id": "ACT_02", "name": "Weekly Visitor", "description": "Logged in 7 times.", "condition": lambda u, c: getattr(u, 'signed_in', 0) >= 7},
        {"id": "ACT_03", "name": "Consistent Developer", "description": "Logged in 30 times.", "condition": lambda u, c: getattr(u, 'signed_in', 0) >= 30},
        {"id": "ACT_04", "name": "Habit Builder", "description": "Logged in 100 times.", "condition": lambda u, c: getattr(u, 'signed_in', 0) >= 100},
        {"id": "ACT_05", "name": "Never Give Up", "description": "Logged in 365 times.", "condition": lambda u, c: getattr(u, 'signed_in', 0) >= 365}
    ],
    "📅 Account Age": [
        {"id": "AGE_01", "name": "One Week Strong", "description": "Account is 7 days old.", "condition": lambda u, c: u.joined_at and (datetime.utcnow() - u.joined_at).days >= 7},
        {"id": "AGE_02", "name": "One Month Strong", "description": "Account is 30 days old.", "condition": lambda u, c: u.joined_at and (datetime.utcnow() - u.joined_at).days >= 30},
        {"id": "AGE_03", "name": "Quarter Veteran", "description": "Account is 90 days old.", "condition": lambda u, c: u.joined_at and (datetime.utcnow() - u.joined_at).days >= 90},
        {"id": "AGE_04", "name": "One Year Later", "description": "Completed one year on Afflux.", "condition": lambda u, c: u.joined_at and (datetime.utcnow() - u.joined_at).days >= 365},
        {"id": "AGE_05", "name": "Platform Veteran", "description": "Completed two years.", "condition": lambda u, c: u.joined_at and (datetime.utcnow() - u.joined_at).days >= 730}
    ],
    "⭐ Level": [
        {"id": "LVL_01", "name": "Level Up!", "description": "Reached Level 5.", "condition": lambda u, c: getattr(u, 'level', 1) >= 5},
        {"id": "LVL_02", "name": "Skilled Builder", "description": "Reached Level 25.", "condition": lambda u, c: getattr(u, 'level', 1) >= 25},
        {"id": "LVL_03", "name": "Elite Developer", "description": "Reached Level 50.", "condition": lambda u, c: getattr(u, 'level', 1) >= 50},
        {"id": "LVL_04", "name": "Master Engineer", "description": "Reached Level 100.", "condition": lambda u, c: getattr(u, 'level', 1) >= 100},
        {"id": "LVL_05", "name": "Beyond Limits", "description": "Reached Level 250.", "condition": lambda u, c: getattr(u, 'level', 1) >= 250}
    ],
    "🏆 Events": [
        {"id": "EVT_01", "name": "First Challenge", "description": "Joined your first event.", "condition": lambda u, c: c.get('events_joined', 0) >= 1},
        {"id": "EVT_02", "name": "Explorer", "description": "Joined 5 events.", "condition": lambda u, c: c.get('events_joined', 0) >= 5},
        {"id": "EVT_03", "name": "Challenger", "description": "Joined 10 events.", "condition": lambda u, c: c.get('events_joined', 0) >= 10},
        {"id": "EVT_04", "name": "Marathon Coder", "description": "Joined 50 events.", "condition": lambda u, c: c.get('events_joined', 0) >= 50},
        {"id": "EVT_05", "name": "Event Machine", "description": "Joined 100 events.", "condition": lambda u, c: c.get('events_joined', 0) >= 100}
    ],
    "📜 Certificates": [
        {"id": "CRT_01", "name": "Certified", "description": "Earned your first certificate.", "condition": lambda u, c: c.get('certs_count', 0) >= 1},
        {"id": "CRT_02", "name": "Knowledge Collector", "description": "Collected 5 certificates.", "condition": lambda u, c: c.get('certs_count', 0) >= 5},
        {"id": "CRT_03", "name": "Achievement Hunter", "description": "Collected 10 certificates.", "condition": lambda u, c: c.get('certs_count', 0) >= 10},
        {"id": "CRT_04", "name": "Credential Master", "description": "Collected 25 certificates.", "condition": lambda u, c: c.get('certs_count', 0) >= 25},
        {"id": "CRT_05", "name": "Hall of Certificates", "description": "Collected 50 certificates.", "condition": lambda u, c: c.get('certs_count', 0) >= 50}
    ],
    "🥇 Competition Results": [
        {"id": "CMP_01", "name": "On the Podium", "description": "Won your first event.", "condition": lambda u, c: c.get('wins_count', 0) >= 1},
        {"id": "CMP_02", "name": "Champion", "description": "Secured first place.", "condition": lambda u, c: c.get('first_places', 0) >= 1},
        {"id": "CMP_03", "name": "Runner-Up", "description": "Secured second place.", "condition": lambda u, c: c.get('second_places', 0) >= 1},
        {"id": "CMP_04", "name": "Bronze Builder", "description": "Secured third place.", "condition": lambda u, c: c.get('third_places', 0) >= 1},
        {"id": "CMP_05", "name": "Trophy Cabinet", "description": "Won 10 competitions.", "condition": lambda u, c: c.get('wins_count', 0) >= 10}
    ],
    "🚀 XP": [
        {"id": "XP_01", "name": "First XP", "description": "Earned your first XP.", "condition": lambda u, c: getattr(u, 'xp', 0) > 0},
        {"id": "XP_02", "name": "Growing Fast", "description": "Earned 1,000 XP.", "condition": lambda u, c: getattr(u, 'xp', 0) >= 1000},
        {"id": "XP_03", "name": "Rising Star", "description": "Earned 10,000 XP.", "condition": lambda u, c: getattr(u, 'xp', 0) >= 10000},
        {"id": "XP_04", "name": "XP Legend", "description": "Earned 50,000 XP.", "condition": lambda u, c: getattr(u, 'xp', 0) >= 50000}
    ],
    "👥 Community": [
        {"id": "COM_01", "name": "Social Developer", "description": "Added your GitHub.", "condition": lambda u, c: bool(u.github)},
        {"id": "COM_02", "name": "Network Builder", "description": "Added LinkedIn.", "condition": lambda u, c: bool(u.linkedin)},
        {"id": "COM_03", "name": "Portfolio Ready", "description": "Added personal website.", "condition": lambda u, c: bool(u.website)},
        {"id": "COM_04", "name": "Open to Connect", "description": "Filled every social link.", "condition": lambda u, c: all([getattr(u, 'github', None),getattr(u, 'linkedin', None),getattr(u, 'website', None),getattr(u, 'instagram', None),getattr(u, 'youtube', None)])}
    ],
    "💎 Rare / Secret": [
        {"id": "SEC_01", "name": "Midnight Coder", "description": "Logged in between 12–4 AM.", "condition": lambda u, c: 0 <= c.get('current_hour', -1) <= 4},
        {"id": "SEC_02", "name": "Early Bird", "description": "Logged in before 6 AM.", "condition": lambda u, c: 4 <= c.get('current_hour', -1) < 6},
        {"id": "SEC_03", "name": "Speed Runner", "description": "Completed profile within 5 minutes of account creation.", "condition": lambda u, c: u.joined_at and all([u.name, u.bio, u.github]) and (datetime.utcnow() - u.joined_at).total_seconds() <= 300},
        {"id": "SEC_04", "name": "Lucky Number", "description": "User ID is a palindrome.", "condition": lambda u, c: str(u.id) == str(u.id)[::-1]},
        {"id": "SEC_05", "name": "OG Member", "description": "Among the first 100 users.", "condition": lambda u, c: u.id <= 100},
        {"id": "SEC_06", "name": "Anniversary Login", "description": "Logged in on your account anniversary.", "condition": lambda u, c: u.joined_at and datetime.utcnow().month == u.joined_at.month and datetime.utcnow().day == u.joined_at.day},
        {"id": "SEC_07", "name": "Comeback", "description": "Returned after 30+ days away.", "condition": lambda u, c: getattr(u, 'days_away', 0) >= 30}
    ]
}
