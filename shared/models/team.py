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
    """
    __tablename__ = "teams"
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    team_type = Column(String(50), nullable=True, default=TeamType.CUSTOM.value)
    
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    lead_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    settings = Column(JSONB, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams"
    )
    user_teams: Mapped[List["UserTeam"]] = relationship(
        "UserTeam",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    children: Mapped[List["Team"]] = relationship(
        "Team",
        backref="parent",
        remote_side="Team.id"
    )
    
    def __repr__(self):
        return f"<Team(name='{self.name}', org={self.organization_id})>"


class UserTeam(Base, UUIDMixin, TimestampMixin):
    """
    Team membership - links users to teams.
    """
    __tablename__ = "user_teams"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    team_role = Column(String(50), nullable=True, default=TeamRole.MEMBER.value)
    
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    left_at = Column(DateTime(timezone=True), nullable=True)
    added_by_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="user_teams")
    user: Mapped["User"] = relationship("User", back_populates="user_teams")
    
    def __repr__(self):
        return f"<UserTeam(team={self.team_id}, user={self.user_id})>"

