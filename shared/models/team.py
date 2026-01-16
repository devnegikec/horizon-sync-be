"""Team model for organizing users within an organization."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship

from shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from shared.models.organization import Organization
    from shared.models.user import User


class TeamRole(str, enum.Enum):
    """Role within a team."""
    LEADER = "leader"
    MEMBER = "member"
    OBSERVER = "observer"


class TeamType(str, enum.Enum):
    """Type of team."""
    SALES = "sales"
    SUPPORT = "support"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    ENGINEERING = "engineering"
    CUSTOM = "custom"


class Team(Base, UUIDMixin, TimestampMixin):
    """
    Team model - groups users within an organization.
    Teams can be hierarchical (parent-child).
    """
    __tablename__ = "teams"
    
    # Organization
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Team info
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Type
    team_type = Column(
        Enum(TeamType),
        default=TeamType.CUSTOM,
        nullable=False
    )
    
    # Hierarchy (self-referential for parent teams)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Team lead (optional)
    lead_user_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Settings
    settings = Column(JSONB, default=dict)
    # Example settings:
    # {
    #     "auto_assign_leads": true,
    #     "visibility": "organization",  # or "team_only"
    #     "max_members": 50
    # }
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams"
    )
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    children: Mapped[List["Team"]] = relationship(
        "Team",
        backref="parent",
        remote_side="Team.id"
    )
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint(
            'organization_id', 'code',
            name='uq_team_org_code'
        ),
    )
    
    @property
    def member_count(self) -> int:
        """Get number of members in this team."""
        return len([m for m in self.members if m.is_active])
    
    def __repr__(self):
        return f"<Team(name='{self.name}', org={self.organization_id})>"


class TeamMember(Base, UUIDMixin, TimestampMixin):
    """
    Team membership - links users to teams with roles.
    """
    __tablename__ = "team_members"
    
    # Foreign keys
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Role in team
    role = Column(
        Enum(TeamRole),
        default=TeamRole.MEMBER,
        nullable=False
    )
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Dates
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Added by
    added_by_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, default=dict)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_member'),
    )
    
    def __repr__(self):
        return f"<TeamMember(team={self.team_id}, user={self.user_id}, role={self.role})>"
