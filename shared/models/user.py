"""User model and related tables."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.organization import Organization
    from shared.models.role import Role
    from shared.models.team import TeamMember


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserType(str, enum.Enum):
    """Type of user account."""
    REGULAR = "regular"
    SERVICE_ACCOUNT = "service_account"
    SYSTEM = "system"


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model - represents a person in the system.
    Users can belong to multiple organizations.
    """
    __tablename__ = "users"
    
    # Identity
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Null for SSO users
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Account type
    user_type = Column(
        Enum(UserType),
        default=UserType.REGULAR,
        nullable=False
    )
    
    # Status
    status = Column(
        Enum(UserStatus),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100), nullable=True)
    mfa_backup_codes = Column(JSONB, nullable=True)
    
    # Login tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    preferences = Column(JSONB, default=dict)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization_roles: Mapped[List["UserOrganizationRole"]] = relationship(
        "UserOrganizationRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.display_name:
            return self.display_name
        return self.email.split("@")[0]
    
    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


# Import Integer at module level (was missing)
from sqlalchemy import Integer


class UserOrganizationRole(Base, UUIDMixin, TimestampMixin):
    """
    Maps users to organizations with their roles.
    A user can have different roles in different organizations.
    """
    __tablename__ = "user_organization_roles"
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status
    is_primary = Column(Boolean, default=False)  # Primary organization
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active")  # active, pending, suspended
    
    # Invitation info
    invited_by_id = Column(UUID(as_uuid=True), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organization_roles"
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="user_roles"
    )
    role: Mapped[Optional["Role"]] = relationship("Role")
    
    def __repr__(self):
        return f"<UserOrganizationRole(user={self.user_id}, org={self.organization_id})>"
