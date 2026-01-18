"""Team business logic service."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.team import Team, UserTeam, TeamRole, TeamType
from shared.schemas.team import TeamHierarchy, TeamStats


class TeamService:
    """Service for team operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_teams(
        self,
        organization_id: UUID,
        team_type: Optional[TeamType] = None,
        parent_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
    ) -> List[Team]:
        """List teams for an organization."""
        query = select(Team).where(
            Team.organization_id == organization_id,
            Team.deleted_at.is_(None)
        )
        
        if team_type:
            query = query.where(Team.team_type == team_type)
        
        if parent_id:
            query = query.where(Team.parent_id == parent_id)
        
        if is_active is not None:
            query = query.where(Team.is_active == is_active)
        
        query = query.order_by(Team.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_team(
        self,
        team_id: UUID,
        organization_id: UUID
    ) -> Optional[Team]:
        """Get a team by ID."""
        query = select(Team).where(
            Team.id == team_id,
            Team.organization_id == organization_id,
            Team.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_team_by_code(
        self,
        organization_id: UUID,
        code: str
    ) -> Optional[Team]:
        """Get team by code."""
        query = select(Team).where(
            Team.code == code,
            Team.organization_id == organization_id,
            Team.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_team_with_members(
        self,
        team_id: UUID,
        organization_id: UUID
    ) -> Optional[Team]:
        """Get team with members loaded."""
        query = select(Team).options(
            selectinload(Team.user_teams).selectinload(UserTeam.user)
        ).where(
            Team.id == team_id,
            Team.organization_id == organization_id,
            Team.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_team(
        self,
        organization_id: UUID,
        name: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        team_type: TeamType = TeamType.CUSTOM,
        parent_id: Optional[UUID] = None,
        lead_user_id: Optional[UUID] = None,
        settings: Optional[Dict] = None,
    ) -> Team:
        """Create a new team."""
        team = Team(
            organization_id=organization_id,
            name=name,
            code=code,
            description=description,
            team_type=team_type,
            parent_id=parent_id,
            lead_user_id=lead_user_id,
            settings=settings or {},
        )
        
        self.db.add(team)
        await self.db.flush()
        
        return team
    
    async def update_team(self, team: Team, data: Dict[str, Any]) -> Team:
        """Update team fields."""
        for key, value in data.items():
            if hasattr(team, key) and value is not None:
                setattr(team, key, value)
        
        await self.db.flush()
        return team
    
    async def delete_team(self, team: Team) -> None:
        """Soft delete a team."""
        team.deleted_at = datetime.utcnow()
        team.is_active = False
        await self.db.flush()
    
    async def get_child_teams(self, team_id: UUID) -> List[Team]:
        """Get child teams."""
        query = select(Team).where(
            Team.parent_id == team_id,
            Team.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def add_member(
        self,
        team_id: UUID,
        user_id: UUID,
        role: TeamRole = TeamRole.MEMBER,
        added_by_id: Optional[UUID] = None,
    ) -> UserTeam:
        """Add a member to a team."""
        member = UserTeam(
            team_id=team_id,
            user_id=user_id,
            team_role=role,
            is_active=True,
            joined_at=datetime.utcnow(),
            added_by_id=added_by_id,
        )
        
        self.db.add(member)
        await self.db.flush()
        
        return member
    
    async def get_team_member(
        self,
        team_id: UUID,
        user_id: UUID
    ) -> Optional[UserTeam]:
        """Get team member."""
        query = select(UserTeam).where(
            UserTeam.team_id == team_id,
            UserTeam.user_id == user_id
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def remove_member(self, member: UserTeam) -> None:
        """Remove a team member."""
        member.is_active = False
        member.left_at = datetime.utcnow()
        await self.db.flush()
    
    async def update_member(
        self,
        member: UserTeam,
        data: Dict[str, Any]
    ) -> UserTeam:
        """Update team member."""
        for key, value in data.items():
            if hasattr(member, key) and value is not None:
                setattr(member, key, value)
        
        await self.db.flush()
        return member
    
    async def get_team_hierarchy(
        self,
        organization_id: UUID
    ) -> List[TeamHierarchy]:
        """Build team hierarchy tree."""
        # Get all teams
        teams = await self.list_teams(organization_id)
        
        # Build tree
        team_dict = {team.id: team for team in teams}
        roots = []
        
        for team in teams:
            if team.parent_id is None:
                roots.append(self._build_hierarchy_node(team, team_dict))
        
        return roots
    
    def _build_hierarchy_node(
        self,
        team: Team,
        team_dict: Dict[UUID, Team]
    ) -> TeamHierarchy:
        """Build a hierarchy node recursively."""
        children = []
        for t in team_dict.values():
            if t.parent_id == team.id:
                children.append(self._build_hierarchy_node(t, team_dict))
        
        return TeamHierarchy(
            id=team.id,
            name=team.name,
            team_type=team.team_type,
            member_count=len([m for m in (team.user_teams or []) if m.is_active]),
            children=children,
        )
    
    async def get_team_stats(self, team_id: UUID) -> TeamStats:
        """Get team statistics."""
        # Count members
        member_query = select(func.count()).select_from(UserTeam).where(
            UserTeam.team_id == team_id
        )
        total_members = (await self.db.execute(member_query)).scalar() or 0
        
        active_query = select(func.count()).select_from(UserTeam).where(
            UserTeam.team_id == team_id,
            UserTeam.is_active == True
        )
        active_members = (await self.db.execute(active_query)).scalar() or 0
        
        leader_query = select(func.count()).select_from(UserTeam).where(
            UserTeam.team_id == team_id,
            UserTeam.team_role == TeamRole.LEADER,
            UserTeam.is_active == True
        )
        leaders = (await self.db.execute(leader_query)).scalar() or 0
        
        return TeamStats(
            total_members=total_members,
            active_members=active_members,
            leaders=leaders,
            total_leads_assigned=0,  # Would need cross-service query
            total_deals=0,
            total_tickets=0,
            conversion_rate=0.0,
        )
