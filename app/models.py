"""Database models for the Research Cloud Portal."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """Researcher user account."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    jobs = db.relationship("Job", backref="user", lazy="dynamic", order_by="Job.created_at.desc()")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Job(db.Model):
    """Compute job request."""

    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # VM configuration
    vm_name = db.Column(db.String(100))
    os_image = db.Column(db.String(50), nullable=False)
    cpu = db.Column(db.Integer, nullable=False, default=1)
    ram = db.Column(db.Integer, nullable=False, default=1024)  # in MB
    storage = db.Column(db.Integer, nullable=False, default=10)  # in GB
    gpu = db.Column(db.Boolean, default=False)
    software_stack = db.Column(db.String(50), nullable=False)

    # Dataset
    dataset_filename = db.Column(db.String(255))
    dataset_path = db.Column(db.String(500))

    # Status tracking
    status = db.Column(db.String(20), default="pending")  # pending, provisioning, running, completed, failed
    vm_id = db.Column(db.Integer)  # OpenNebula VM ID
    vm_ip = db.Column(db.String(45))  # VM IP address
    result_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    @property
    def status_color(self):
        """Return CSS color class for the status."""
        colors = {
            "pending": "status-pending",
            "provisioning": "status-provisioning",
            "running": "status-running",
            "completed": "status-completed",
            "failed": "status-failed",
        }
        return colors.get(self.status, "status-pending")

    @property
    def status_icon(self):
        """Return icon for the status."""
        icons = {
            "pending": "⏳",
            "provisioning": "🔄",
            "running": "⚡",
            "completed": "✅",
            "failed": "❌",
        }
        return icons.get(self.status, "⏳")

    @property
    def ram_display(self):
        """Return human-readable RAM."""
        if self.ram >= 1024:
            return f"{self.ram // 1024} GB"
        return f"{self.ram} MB"

    def __repr__(self):
        return f"<Job {self.id} [{self.status}]>"
