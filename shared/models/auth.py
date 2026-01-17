"""Authentication-related models."""
import enum
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from shared.models.user import User
    from shared.models.organization import Organization
    from shared.models.role import Role


class RefreshToken(Base, UUIDMixin):
    """
    Refresh token storage for JWT authentication.
    Allows token rotation and revocation.
    """
    __tablename__ = "refresh_tokens"
    
    # User
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    token_family = Column(String(100), nullable=True, index=True)  # For token rotation
    
    # Device info
    device_id = Column(String(100), nullable=True)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    os_info = Column(String(100), nullable=True)
    browser_info = Column(String(100), nullable=True)
    
    # Request context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Validity
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        now = datetime.utcnow()
        return self.revoked_at is None and self.expires_at > now
    
    def revoke(self, reason: str = "manual"):
        """Revoke this token."""
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason
    
    def __repr__(self):
        return f"<RefreshToken(user={self.user_id}, valid={self.is_valid})>"


class PasswordReset(Base, UUIDMixin):
    """
    Password reset token storage.
    """
    __tablename__ = "password_resets"
    
    # User
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Request context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Validity
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    @property
    def is_valid(self) -> bool:
        """Check if reset token is still valid."""
        now = datetime.utcnow()
        return self.used_at is None and self.expires_at > now
    
    def __repr__(self):
        return f"<PasswordReset(user={self.user_id}, valid={self.is_valid})>"


class InvitationStatus(str, enum.Enum):
    """Invitation status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invitation(Base, UUIDMixin):
    """
    User invitation to join an organization.
    """
    __tablename__ = "invitations"
    
    # Organization
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Invitee
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Assigned role
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Teams to add to (optional)
    team_ids = Column(JSONB, nullable=True)
    
    # Inviter
    invited_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    status = Column(
        String(20),
        default=InvitationStatus.PENDING.value,
        nullable=False,
        index=True
    )
    
    # Validity
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Usage
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_user_id = Column(UUID(as_uuid=True), nullable=True)  # User created from invitation
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Optional message
    message = Column(Text, nullable=True)
    
    # Metadata
    extra_data = Column(JSONB, default=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if invitation is still valid."""
        now = datetime.utcnow()
        return (
            self.status == InvitationStatus.PENDING.value and
            self.expires_at > now
        )
    
    def accept(self, user_id):
        """Mark invitation as accepted."""
        self.status = InvitationStatus.ACCEPTED.value
        self.accepted_at = datetime.utcnow()
        self.accepted_user_id = user_id
    
    def revoke(self):
        """Revoke the invitation."""
        self.status = InvitationStatus.REVOKED.value
    
    # Indexes
    __table_args__ = (
        Index('ix_invitation_org_email', 'organization_id', 'email'),
    )
    
    def __repr__(self):
        return f"<Invitation(email='{self.email}', org={self.organization_id}, status={self.status})>"


class EmailVerification(Base, UUIDMixin):
    """
    Email verification token storage.
    """
    __tablename__ = "email_verifications"
    
    # User
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Email to verify (in case user changes email)
    email = Column(String(255), nullable=False)
    
    # Token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Validity
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    @property
    def is_valid(self) -> bool:
        """Check if verification token is still valid."""
        now = datetime.utcnow()
        return self.verified_at is None and self.expires_at > now
    
    def __repr__(self):
        return f"<EmailVerification(email='{self.email}', valid={self.is_valid})>"
