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
    from shared.models.user import User
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
    All data is isolated by organization_id.
    """
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=True, index=True)
    status = Column(String(50), nullable=True, default=OrganizationStatus.ACTIVE.value)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    address = Column(Text, nullable=True)
    settings = Column(JSONB, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
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
        return f"<Organization(id={self.id}, name='{self.name}')>"


# Note: OrganizationSettings, OrganizationStatus, OrganizationType removed to strictly follow DBML
# but they can be added back if needed as extensions.

