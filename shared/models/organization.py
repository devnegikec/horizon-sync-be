"""Organization model - represents a tenant/company in the system."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.subscription import Subscription
    from shared.models.user import UserOrganizationRole
    from shared.models.role import Role
    from shared.models.team import Team


class OrganizationStatus(str, enum.Enum):
    """Organization status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class OrganizationType(str, enum.Enum):
    """Organization type enum."""
    STARTUP = "startup"
    SMB = "smb"
    ENTERPRISE = "enterprise"
    NON_PROFIT = "non_profit"


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    Organization model - represents a tenant/company.
    All CRM data is isolated by organization_id.
    """
    __tablename__ = "organizations"
    
    # Basic info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Contact info
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business info
    organization_type = Column(
        Enum(OrganizationType),
        default=OrganizationType.SMB,
        nullable=False
    )
    industry = Column(String(100), nullable=True)
    tax_id = Column(String(50), nullable=True)
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex color
    
    # Domain & SSO
    domain = Column(String(255), unique=True, nullable=True, index=True)
    sso_enabled = Column(Boolean, default=False)
    sso_provider = Column(String(50), nullable=True)  # google, okta, azure
    sso_config = Column(JSONB, nullable=True)
    
    # Status
    status = Column(
        Enum(OrganizationStatus),
        default=OrganizationStatus.PENDING,
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Settings stored as JSON
    settings = Column(JSONB, default=dict, nullable=False)
    
    # Extra data
    extra_data = Column(JSONB, default=dict, nullable=False)
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    user_roles: Mapped[List["UserOrganizationRole"]] = relationship(
        "UserOrganizationRole",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    teams: Mapped[List["Team"]] = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class OrganizationSettings(Base, UUIDMixin, TimestampMixin):
    """
    Extended organization settings stored separately for performance.
    """
    __tablename__ = "organization_settings"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Locale settings
    timezone = Column(String(50), default="UTC")
    date_format = Column(String(20), default="YYYY-MM-DD")
    time_format = Column(String(10), default="24h")
    currency = Column(String(3), default="USD")
    language = Column(String(10), default="en")
    
    # Feature flags
    features = Column(JSONB, default=dict)
    
    # Notification settings
    notifications = Column(JSONB, default=dict)
    
    # Security settings
    security = Column(JSONB, default=dict)
    
    # Integration settings
    integrations = Column(JSONB, default=dict)
    
    # Custom fields schema
    custom_fields = Column(JSONB, default=dict)
    
    def __repr__(self):
        return f"<OrganizationSettings(org_id={self.organization_id})>"
