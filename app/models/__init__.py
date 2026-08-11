"""Database models for ImpactBridge AI.

Each class maps to a table in the SQLite database. Relationships are
defined with SQLAlchemy ORM and foreign keys so the schema is clean
and the app stays fully database-driven.
"""
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """Registered platform user (volunteer account holder or admin)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="USER")  # USER | ADMIN
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    volunteer_profile = db.relationship(
        "Volunteer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    event_registrations = db.relationship(
        "EventRegistration", back_populates="user", cascade="all, delete-orphan"
    )
    donations = db.relationship("Donation", back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "ADMIN"

    def __repr__(self):
        return f"<User {self.email}>"


class Project(db.Model):
    """Social-impact project run/featured by the organization."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    location = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="ACTIVE", index=True)  # ACTIVE|COMPLETED|PLANNED
    beneficiaries = db.Column(db.Integer, default=0)
    objectives = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    gallery_images = db.relationship("Gallery", back_populates="project", lazy="dynamic")

    def __repr__(self):
        return f"<Project {self.title}>"


class Volunteer(db.Model):
    """Volunteer application / profile linked to a user."""

    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    skills = db.Column(db.Text, nullable=False)
    area_of_interest = db.Column(db.String(80), nullable=False)
    availability = db.Column(db.String(80), nullable=False)
    experience = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="PENDING", index=True)  # PENDING|APPROVED|REJECTED
    admin_notes = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="volunteer_profile")

    def __repr__(self):
        return f"<Volunteer {self.application_id}>"


class Campaign(db.Model):
    """Fundraising / awareness campaign. Donations are DEMO only."""

    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    target_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="ACTIVE", index=True)  # ACTIVE|CLOSED|DRAFT
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donations = db.relationship("Donation", back_populates="campaign", lazy="dynamic")

    @property
    def amount_raised(self) -> float:
        return round(sum(d.amount for d in self.donations), 2)

    @property
    def percentage(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return round(min(self.amount_raised / self.target_amount * 100, 100), 1)

    @property
    def days_remaining(self) -> int:
        delta = (self.end_date - date.today()).days
        return max(delta, 0)

    def __repr__(self):
        return f"<Campaign {self.title}>"


class Donation(db.Model):
    """DEMO donation record – no real payment is processed."""

    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    donor_name = db.Column(db.String(120), nullable=False)
    donor_email = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=True)
    demo = db.Column(db.Boolean, default=True)  # always True – academic project
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    campaign = db.relationship("Campaign", back_populates="donations")
    user = db.relationship("User", back_populates="donations")

    def __repr__(self):
        return f"<Donation {self.transaction_id}>"


class Event(db.Model):
    """Volunteering / awareness event."""

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    event_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(10), nullable=True)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="OPEN", index=True)  # OPEN|CLOSED|FULL
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship(
        "EventRegistration", back_populates="event", cascade="all, delete-orphan"
    )

    @property
    def registrations_count(self) -> int:
        return len(self.registrations)

    @property
    def remaining_seats(self) -> int:
        return max(self.capacity - self.registrations_count, 0)

    @property
    def is_full(self) -> bool:
        return self.registrations_count >= self.capacity

    def __repr__(self):
        return f"<Event {self.title}>"


class EventRegistration(db.Model):
    """Join table for user → event registration (unique per user+event)."""

    __tablename__ = "event_registrations"
    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", name="uq_user_event"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="event_registrations")
    event = db.relationship("Event", back_populates="registrations")

    def __repr__(self):
        return f"<EventRegistration user={self.user_id} event={self.event_id}>"


class Gallery(db.Model):
    """Project photographs / gallery item."""

    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="gallery_images")

    def __repr__(self):
        return f"<Gallery {self.image}>"


class ImpactMetric(db.Model):
    """Yearly / monthly impact statistics. Drives the Impact dashboard."""

    __tablename__ = "impact_metrics"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=True)  # optional
    beneficiaries = db.Column(db.Integer, default=0)
    volunteers = db.Column(db.Integer, default=0)
    projects = db.Column(db.Integer, default=0)
    funds_raised = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<ImpactMetric {self.year}-{self.month}>"


class ContactMessage(db.Model):
    """Messages submitted through the public contact form."""

    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ContactMessage {self.subject}>"


class AIConversation(db.Model):
    """ImpactBot conversation log."""

    __tablename__ = "ai_conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(20), default="ollama")  # ollama | fallback
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class AuditResult(db.Model):
    """Website health audit (one row per audit run)."""

    __tablename__ = "audit_results"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False, index=True)
    overall_score = db.Column(db.Integer, default=0)
    seo_score = db.Column(db.Integer, default=0)
    accessibility_score = db.Column(db.Integer, default=0)
    links_score = db.Column(db.Integer, default=0)
    security_score = db.Column(db.Integer, default=0)
    performance_score = db.Column(db.Integer, default=0)
    content_score = db.Column(db.Integer, default=0)
    grade = db.Column(db.String(30), default="Needs Improvement")
    ai_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditIssue(db.Model):
    """Individual issue found during an audit. Linked to an AuditResult."""

    __tablename__ = "audit_issues"

    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey("audit_results.id"), nullable=False)
    category = db.Column(db.String(30), nullable=False)  # seo, accessibility, links...
    severity = db.Column(db.String(20), default="MEDIUM")  # CRITICAL|HIGH|MEDIUM|LOW
    title = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)

    audit = db.relationship("AuditResult", backref="issues")

    def __repr__(self):
        return f"<AuditIssue {self.category}: {self.title}>"