"""User model and related tables."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.organization import Organization
    from shared.models.role import Role
    from shared.models.team import UserTeam


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


class UserOrganizationRole(Base, UUIDMixin):
    """
    Maps users to roles within an organization.
    """
    __tablename__ = "user_organization_roles"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), nullable=True, default="active")
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role")
    
    def __repr__(self):
        return f"<UserOrganizationRole(user={self.user_id}, role={self.role_id})>"


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model - represents a person in the system.
    Users belong to a single organization.
    """
    __tablename__ = "users"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Identity
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Settings
    timezone = Column(String(50), nullable=True, default="UTC")
    language = Column(String(10), nullable=True, default="en")
    preferences = Column(JSONB, nullable=True, default=dict)
    
    # Account type
    user_type = Column(String(50), nullable=True, default=UserType.REGULAR.value)
    
    # Status
    status = Column(String(50), nullable=True, default=UserStatus.ACTIVE.value)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Login security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    
    # MFA
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(100), nullable=True)
    mfa_backup_codes = Column(JSONB, nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="users"
    )
    user_roles: Mapped[List["UserOrganizationRole"]] = relationship(
        "UserOrganizationRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    user_teams: Mapped[List["UserTeam"]] = relationship(
        "UserTeam",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

    @property
    def is_locked(self) -> bool:
        """Check if user account is currently locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
