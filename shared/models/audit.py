"""Audit and Activity logging models."""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from shared.database.base import Base, UUIDMixin


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    PERMISSION_CHANGE = "permission_change"
    SETTING_CHANGE = "setting_change"
    SUBSCRIPTION_CHANGE = "subscription_change"


class ActivityLog(Base, UUIDMixin):
    """
    Activity log - user-facing activity feed.
    """
    __tablename__ = "activity_logs"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    action = Column(String(100), nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action})>"


class AuditLog(Base, UUIDMixin):
    """
    Audit log - system-level tracking.
    """
    __tablename__ = "audit_logs"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    operation = Column(String(100), nullable=True)
    entity = Column(String(100), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    previous_data = Column(Text, nullable=True)
    new_data = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, operation={self.operation})>"

