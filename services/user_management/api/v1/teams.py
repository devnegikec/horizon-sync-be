"""Team management endpoints."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.models.team import Team, TeamMember, TeamRole, TeamType
from shared.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamDetailResponse,
    TeamMemberAdd,
    TeamMemberBulkAdd,
    TeamMemberUpdate,
    TeamMemberResponse,
    TeamListFilter,
    TeamHierarchy,
    TeamStats,
)
from shared.schemas.common import SuccessResponse, PaginatedResponse
from shared.security.jwt import TokenPayload
from services.user_management.services.team_service import TeamService

router = APIRouter()


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    team_type: Optional[TeamType] = Query(None),
    parent_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all teams in the organization."""
    team_service = TeamService(db)
    
    teams = await team_service.list_teams(
        organization_id=tenant_id,
        team_type=team_type,
        parent_id=parent_id,
        is_active=is_active,
    )
    
    return [TeamResponse.model_validate(team) for team in teams]


@router.get("/hierarchy", response_model=List[TeamHierarchy])
async def get_team_hierarchy(
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get team hierarchy tree."""
    team_service = TeamService(db)
    
    hierarchy = await team_service.get_team_hierarchy(tenant_id)
    
    return hierarchy


@router.post("", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    current_user: TokenPayload = Depends(require_permissions("team:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new team."""
    team_service = TeamService(db)
    
    # Check if code already exists (if provided)
    if team_data.code:
        existing = await team_service.get_team_by_code(tenant_id, team_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team with code '{team_data.code}' already exists"
            )
    
    # Create team
    team = await team_service.create_team(
        organization_id=tenant_id,
        name=team_data.name,
        code=team_data.code,
        description=team_data.description,
        team_type=team_data.team_type,
        parent_id=team_data.parent_id,
        lead_user_id=team_data.lead_user_id,
        settings=team_data.settings,
    )
    
    # Add initial members if provided
    if team_data.member_ids:
        for member_id in team_data.member_ids:
            await team_service.add_member(team.id, member_id, TeamRole.MEMBER)
    
    await db.commit()
    
    return TeamResponse.model_validate(team)


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get team details with members."""
    team_service = TeamService(db)
    
    team = await team_service.get_team_with_members(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return TeamDetailResponse.model_validate(team)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    update_data: TeamUpdate,
    current_user: TokenPayload = Depends(require_permissions("team:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a team."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Update team
    updated_team = await team_service.update_team(
        team, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return TeamResponse.model_validate(updated_team)


@router.delete("/{team_id}", response_model=SuccessResponse)
async def delete_team(
    team_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("team:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a team."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check for child teams
    children = await team_service.get_child_teams(team_id)
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete team with child teams. Delete or reassign child teams first."
        )
    
    # Soft delete
    await team_service.delete_team(team)
    
    await db.commit()
    
    return SuccessResponse(message="Team deleted successfully")


@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: UUID,
    member_data: TeamMemberAdd,
    current_user: TokenPayload = Depends(require_permissions("team:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Add a member to a team."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user already in team
    existing = await team_service.get_team_member(team_id, member_data.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this team"
        )
    
    # Add member
    member = await team_service.add_member(
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role,
        added_by_id=UUID(current_user.sub),
    )
    
    await db.commit()
    
    return TeamMemberResponse.model_validate(member)


@router.post("/{team_id}/members/bulk", response_model=SuccessResponse)
async def add_team_members_bulk(
    team_id: UUID,
    members_data: TeamMemberBulkAdd,
    current_user: TokenPayload = Depends(require_permissions("team:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Add multiple members to a team."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    added_count = 0
    for user_id in members_data.user_ids:
        existing = await team_service.get_team_member(team_id, user_id)
        if not existing:
            await team_service.add_member(
                team_id=team_id,
                user_id=user_id,
                role=members_data.role,
                added_by_id=UUID(current_user.sub),
            )
            added_count += 1
    
    await db.commit()
    
    return SuccessResponse(message=f"Added {added_count} members to team")


@router.delete("/{team_id}/members/{user_id}", response_model=SuccessResponse)
async def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("team:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Remove a member from a team."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    member = await team_service.get_team_member(team_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Remove member
    await team_service.remove_member(member)
    
    await db.commit()
    
    return SuccessResponse(message="Member removed from team")


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: UUID,
    user_id: UUID,
    update_data: TeamMemberUpdate,
    current_user: TokenPayload = Depends(require_permissions("team:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a team member's role."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    member = await team_service.get_team_member(team_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Update member
    updated_member = await team_service.update_member(
        member, update_data.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    return TeamMemberResponse.model_validate(updated_member)


@router.get("/{team_id}/stats", response_model=TeamStats)
async def get_team_stats(
    team_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get team statistics."""
    team_service = TeamService(db)
    
    team = await team_service.get_team(team_id, tenant_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    stats = await team_service.get_team_stats(team_id)
    
    return stats
