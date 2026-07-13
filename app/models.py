from app.extensions import db
from sqlalchemy.sql import func
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = "users"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile Information
    name = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)  # Cloudinary path/URL
    resume = db.Column(db.String(255), nullable=True)       # Cloudinary path/URL
    bio = db.Column(db.String(300), nullable=True)

    # Social Links
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)

    # Gamification
    level = db.Column(db.Integer, nullable=False, default=0)
    exp = db.Column(db.Integer, nullable=False, default=0)

    # Statistics
    events_participated = db.Column(db.Integer, nullable=False, default=0)
    events_won = db.Column(db.Integer, nullable=False, default=0)
    certificates_count = db.Column(db.Integer, nullable=False, default=0)

    # Badges & Verification
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

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


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(300))
    
    category = db.Column(db.String(50), nullable=False) 
    # Options: hackathon, quiz, webinar, scholarship, cultural, competition
    
    mode = db.Column(db.String(20), default="online") 
    # Options: online, offline, hybrid
    
    hosted_by = db.Column(db.String(100), default="Afflux")

    # 🕒 Detailed Dynamic Timeline Windows (Timezone-Aware)
    registration_start = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)  # 💡 Also acts as Execution & Submission Start!
    event_start_date = db.Column(db.DateTime)
    submission_deadline = db.Column(db.DateTime)

    # 🔗 Network Endpoints
    registration_url = db.Column(db.String(500))
    submit_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def status(self):
        """Calculates overarching status dynamically using timezone-aware logic."""
        now = datetime.now(timezone.utc)
        
        reg_deadline = self.registration_deadline.replace(tzinfo=timezone.utc) if self.registration_deadline and self.registration_deadline.tzinfo is None else self.registration_deadline
        reg_start = self.registration_start.replace(tzinfo=timezone.utc) if self.registration_start and self.registration_start.tzinfo is None else self.registration_start
        sub_deadline = self.submission_deadline.replace(tzinfo=timezone.utc) if self.submission_deadline and self.submission_deadline.tzinfo is None else self.submission_deadline

        if sub_deadline and now >= sub_deadline:
            return "closed"
        elif reg_start and now < reg_start:
            return "upcoming"
        return "open"

    @property
    def execution_started(self):
        """Returns True if registration has closed, meaning execution/submission phase is officially active."""
        now = datetime.now(timezone.utc)
        reg_deadline = self.registration_deadline.replace(tzinfo=timezone.utc) if self.registration_deadline and self.registration_deadline.tzinfo is None else self.registration_deadline
        
        return reg_deadline is not None and now >= reg_deadline

    @property
    def submission_open(self):
        """Returns True if the hackathon execution timeline is live and final deadline has not passed."""
        if not self.execution_started:
            return False

        now = datetime.now(timezone.utc)
        sub_deadline = self.submission_deadline.replace(tzinfo=timezone.utc) if self.submission_deadline and self.submission_deadline.tzinfo is None else self.submission_deadline

        if sub_deadline and now > sub_deadline:
            return False
        return True