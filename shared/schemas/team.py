"""Team Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from shared.models.team import TeamRole, TeamType
from shared.schemas.common import BaseSchema
from shared.schemas.user import UserResponse


class TeamBase(BaseSchema):
    """Base team schema."""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: Optional[str] = Field(default=None, max_length=50, pattern="^[a-z0-9_-]+$")
    description: Optional[str] = None
    team_type: Optional[TeamType] = TeamType.CUSTOM


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    
    parent_id: Optional[UUID] = None
    lead_user_id: Optional[UUID] = None
    member_ids: Optional[List[UUID]] = None
    settings: Optional[Dict[str, Any]] = None


class TeamUpdate(BaseSchema):
    """Schema for updating a team."""
    
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    team_type: Optional[TeamType] = None
    parent_id: Optional[UUID] = None
    lead_user_id: Optional[UUID] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    """Schema for team response."""
    
    id: UUID
    organization_id: UUID
    parent_id: Optional[UUID] = None
    lead_user_id: Optional[UUID] = None
    is_active: bool
    member_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # Optional nested info
    lead_user: Optional[Dict[str, Any]] = None
    parent_team: Optional[Dict[str, Any]] = None


class TeamDetailResponse(TeamResponse):
    """Detailed team response with members."""
    
    members: List["TeamMemberResponse"]
    children: List["TeamResponse"] = []
    settings: Dict[str, Any] = {}


class TeamMemberBase(BaseSchema):
    """Base team member schema."""
    
    user_id: UUID
    role: TeamRole = TeamRole.MEMBER


class TeamMemberAdd(TeamMemberBase):
    """Schema for adding a team member."""
    pass


class TeamMemberBulkAdd(BaseSchema):
    """Schema for bulk adding team members."""
    
    user_ids: List[UUID]
    role: TeamRole = TeamRole.MEMBER


class TeamMemberUpdate(BaseSchema):
    """Schema for updating a team member."""
    
    role: Optional[TeamRole] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseSchema):
    """Schema for team member response."""
    
    id: UUID
    team_id: UUID
    user_id: UUID
    role: TeamRole
    is_active: bool
    joined_at: datetime
    
    # User info (optionally included)
    user: Optional[Dict[str, Any]] = None


class TeamListFilter(BaseSchema):
    """Filter parameters for listing teams."""
    
    search: Optional[str] = None
    team_type: Optional[TeamType] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    has_members: Optional[bool] = None


class TeamHierarchy(BaseSchema):
    """Team hierarchy response."""
    
    id: UUID
    name: str
    team_type: TeamType
    member_count: int
    children: List["TeamHierarchy"] = []


class TeamStats(BaseSchema):
    """Team statistics."""
    
    total_members: int
    active_members: int
    leaders: int
    
    # Performance metrics (CRM related)
    total_leads_assigned: int = 0
    total_deals: int = 0
    total_tickets: int = 0
    conversion_rate: float = 0.0


# For self-referential type hints
TeamHierarchy.model_rebuild()
TeamDetailResponse.model_rebuild()
