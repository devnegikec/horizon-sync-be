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


class AuditLog(Base, UUIDMixin):
    """
    Audit log - tracks all significant actions for compliance and security.
    Immutable records - never update or delete.
    """
    __tablename__ = "audit_logs"
    
    # Organization context
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Who performed the action
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    user_email = Column(String(255), nullable=True)  # Preserved even if user deleted
    
    # What action was performed
    action = Column(Enum(AuditAction), nullable=False, index=True)
    
    # On what resource
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)  # Human-readable name
    
    # Change details
    old_values = Column(JSONB, nullable=True)  # Previous state
    new_values = Column(JSONB, nullable=True)  # New state
    changed_fields = Column(JSONB, nullable=True)  # List of changed field names
    
    # Request context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)  # For tracing
    
    # Additional context
    extra_data = Column(JSONB, default=dict)
    description = Column(Text, nullable=True)  # Human-readable description
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_audit_org_created', 'organization_id', 'created_at'),
        Index('ix_audit_user_created', 'user_id', 'created_at'),
        Index('ix_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, resource={self.resource_type}:{self.resource_id})>"


class ActivityType(str, enum.Enum):
    """Types of user activities for activity feed."""
    # Leads
    LEAD_CREATED = "lead_created"
    LEAD_UPDATED = "lead_updated"
    LEAD_CONVERTED = "lead_converted"
    LEAD_ASSIGNED = "lead_assigned"
    
    # Contacts
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    
    # Deals
    DEAL_CREATED = "deal_created"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"
    
    # Tickets
    TICKET_CREATED = "ticket_created"
    TICKET_ASSIGNED = "ticket_assigned"
    TICKET_RESOLVED = "ticket_resolved"
    TICKET_ESCALATED = "ticket_escalated"
    
    # Communication
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    CALL_LOGGED = "call_logged"
    NOTE_ADDED = "note_added"
    
    # Tasks
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    
    # System
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    COMMENT_ADDED = "comment_added"


class ActivityLog(Base, UUIDMixin):
    """
    Activity log - user-facing activity feed.
    Less technical than audit logs, meant for CRM activity tracking.
    """
    __tablename__ = "activity_logs"
    
    # Organization context
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Who performed the action
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Activity type
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    
    # Related entity
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_name = Column(String(255), nullable=True)
    
    # Related secondary entity (e.g., lead converted to contact)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Team context (optional)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Activity details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    
    # Visibility
    is_public = Column(String, default=True)  # Visible to all org members
    visible_to_teams = Column(JSONB, nullable=True)  # Array of team IDs
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_activity_org_created', 'organization_id', 'created_at'),
        Index('ix_activity_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<ActivityLog(type={self.activity_type}, entity={self.entity_type}:{self.entity_id})>"
