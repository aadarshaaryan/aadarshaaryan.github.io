from app.extensions import db
from sqlalchemy.sql import func
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile Information
    name = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(300), nullable=True)

    # Social Links
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)

    # Badges & Verification
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # xp points
    last_signed_in = db.Column(db.Integer, nullable=True)
    signed_in = db.Column(db.Integer, nullable=False, default=0)
    xp = db.Column(db.Integer, nullable=False, default=0)

    ######
    achievements = db.Column(db.JSON, default=dict, nullable=False)

    # Timestamps
    joined_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    @property
    def level(self):
        xp = self.xp
        # Updated to perfectly match your xp_thresholds array indexes
        if xp >= 10000: return 10
        elif xp >= 7000: return 9
        elif xp >= 5000: return 8
        elif xp >= 3500: return 7
        elif xp >= 2500: return 6
        elif xp >= 1800: return 5
        elif xp >= 1000: return 4
        elif xp >= 550: return 3
        elif xp >= 300: return 2
        elif xp >= 150: return 1
        return 0
    
    @property
    def xp_thresholds(self):
        return [0, 150, 300, 550, 1000, 1800, 2500, 3500, 5000, 7000, 10000]

    @property
    def next_level_xp(self):
        thresholds = self.xp_thresholds
        current_lvl = self.level
        if current_lvl >= 10: return 10000 
        return thresholds[current_lvl + 1]

    @property
    def progress_percentage(self):
        thresholds = self.xp_thresholds
        current_lvl = self.level
        start_xp = thresholds[current_lvl]
        end_xp = self.next_level_xp
        
        # Avoid division by zero error if at max level
        if end_xp == start_xp: return 100.0 
        
        current_level_progress = self.xp - start_xp
        total_needed_for_level = end_xp - start_xp
        
        percentage = (current_level_progress / total_needed_for_level) * 100
        return round(percentage, 1)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(300))
    
    # 🔗 Unique slug for routing
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    
    category = db.Column(db.String(50), nullable=False) 
    mode = db.Column(db.String(20), default="online") 
    hosted_by = db.Column(db.String(100), default="Afflux")

    # Timelines
    registration_start = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    registration_deadline = db.Column(db.DateTime(timezone=True), nullable=False)  
    event_start_date = db.Column(db.DateTime(timezone=True))
    submission_deadline = db.Column(db.DateTime(timezone=True))

    # Endpoints
    registration_url = db.Column(db.String(500))
    submission_url = db.Column(db.String(500))

    created_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    @property
    def status(self):
        now = datetime.now(timezone.utc)
        
        def ensure_utc(dt):
            if dt and dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        reg_start = ensure_utc(self.registration_start)
        sub_deadline = ensure_utc(self.submission_deadline)

        print("NOW:", now)
        print("DEADLINE:", sub_deadline)
        print("Comparison:", now >= sub_deadline)


        if sub_deadline and now >= sub_deadline:
            return "closed"
        
        elif reg_start and now < reg_start:
            return "upcoming"
            
        return "open"


    @property
    def execution_started(self):
        now = datetime.now(timezone.utc)
        reg_deadline = self.registration_deadline.replace(tzinfo=timezone.utc) if self.registration_deadline and self.registration_deadline.tzinfo is None else self.registration_deadline
        return reg_deadline is not None and now >= reg_deadline

    @property
    def submission_open(self):
        if not self.execution_started:
            return False
        # Use timezone-aware UTC now
        now = datetime.now(timezone.utc)
        # Ensure deadline is aware
        sub_deadline = self.submission_deadline
        if sub_deadline.tzinfo is None:
            sub_deadline = sub_deadline.replace(tzinfo=timezone.utc)
            
        return now <= sub_deadline

class EventResult(db.Model):
    __tablename__ = "event_results"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # Participant Information
    participant_name = db.Column(db.String(150), nullable=False)
    participant_email = db.Column(db.String(150), nullable=False, index=True)

    # Team Information (Nullable for solo participants)
    team_name = db.Column(db.String(150), nullable=True)
    team_leader_email = db.Column(db.String(150), nullable=True)

    # Universal Data Bucket (Store all hackathon/quiz/design fields here as JSON)
    submission_data = db.Column(db.JSON, nullable=True)

    # Result Tracking
    # 0 = Participant (Default), 1 = 1st, 2 = 2nd, 3 = 3rd, 4+ = Other Ranks
    position = db.Column(db.Integer, default=0, nullable=False)

    # Certificate Tracking
    certificate_code = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    # Metadata
    submitted_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    event = db.relationship(
        "Event",
        backref=db.backref(
            "results",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "event_results",
            lazy=True
        )
    )