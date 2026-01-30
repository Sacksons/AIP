"""Audit logging model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from app.core.database import Base


class AuditLog(Base):
    """Audit trail for all significant actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)

    # Actor
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    user_email = Column(String(255))  # Stored separately for reference even if user deleted
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))

    # Action details
    action = Column(String(100), nullable=False)  # create, update, delete, view, export, login, etc.
    resource_type = Column(String(100), nullable=False)  # user, project, document, verification, etc.
    resource_id = Column(String(100))  # ID of the affected resource

    # Change tracking
    old_values = Column(JSON)  # Previous state (for updates)
    new_values = Column(JSON)  # New state (for creates/updates)
    changes = Column(JSON)  # Diff of changes

    # Context
    description = Column(Text)  # Human-readable description
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_id = Column(String(36))  # For correlating multiple logs

    # Severity/category
    severity = Column(String(20), default="info")  # info, warning, error, critical
    category = Column(String(50))  # security, data, system, user_action

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.resource_type} by user={self.user_id}>"

    @classmethod
    def log(
        cls,
        db_session,
        action: str,
        resource_type: str,
        user_id: int = None,
        user_email: str = None,
        resource_id: str = None,
        old_values: dict = None,
        new_values: dict = None,
        description: str = None,
        ip_address: str = None,
        severity: str = "info",
        category: str = None,
    ):
        """
        Helper method to create an audit log entry.

        Usage:
            AuditLog.log(
                db,
                action="create",
                resource_type="project",
                user_id=current_user.id,
                resource_id=str(new_project.id),
                new_values={"name": "New Project"},
                description="Created new project"
            )
        """
        log_entry = cls(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            user_email=user_email,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            severity=severity,
            category=category,
        )
        db_session.add(log_entry)
        return log_entry
