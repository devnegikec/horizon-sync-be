"""User business logic service."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.user import User, UserOrganizationRole, UserStatus
from shared.models.organization import Organization
from shared.models.role import Role
from shared.models.auth import Invitation, InvitationStatus
from shared.models.team import Team, TeamMember
from shared.schemas.user import UserListFilter
from shared.schemas.common import PaginatedResponse
from shared.security.password import hash_password, verify_password


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        timezone: str = "UTC",
        **kwargs
    ) -> User:
        """Create a new user."""
        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            timezone=timezone,
            status=UserStatus.PENDING_VERIFICATION,
            preferences={},
            **kwargs
        )
        
        self.db.add(user)
        await self.db.flush()
        
        return user
    
    async def update_user(self, user: User, data: Dict[str, Any]) -> User:
        """Update user fields."""
        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        await self.db.flush()
        return user
    
    async def add_user_to_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
        role_id: Optional[UUID] = None,
        is_primary: bool = False,
    ) -> UserOrganizationRole:
        """Add user to an organization with a role."""
        user_org_role = UserOrganizationRole(
            user_id=user_id,
            organization_id=organization_id,
            role_id=role_id,
            is_primary=is_primary,
            is_active=True,
            status="active",
            joined_at=datetime.utcnow(),
        )
        
        self.db.add(user_org_role)
        await self.db.flush()
        
        return user_org_role
    
    async def get_user_organization_role(
        self,
        user_id: UUID,
        organization_id: UUID
    ) -> Optional[UserOrganizationRole]:
        """Get user's role in an organization."""
        query = select(UserOrganizationRole).options(
            selectinload(UserOrganizationRole.role)
        ).where(
            UserOrganizationRole.user_id == user_id,
            UserOrganizationRole.organization_id == organization_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_organizations(self, user_id: UUID) -> List[Dict]:
        """Get all organizations a user belongs to."""
        query = select(UserOrganizationRole).options(
            selectinload(UserOrganizationRole.organization),
            selectinload(UserOrganizationRole.role)
        ).where(
            UserOrganizationRole.user_id == user_id,
            UserOrganizationRole.is_active == True
        )
        
        result = await self.db.execute(query)
        user_org_roles = result.scalars().all()
        
        return [
            {
                "organization_id": uor.organization_id,
                "organization_name": uor.organization.name if uor.organization else None,
                "organization_slug": uor.organization.slug if uor.organization else None,
                "role_id": str(uor.role_id) if uor.role_id else None,
                "role_name": uor.role.name if uor.role else None,
                "is_primary": uor.is_primary,
                "joined_at": uor.joined_at,
            }
            for uor in user_org_roles
        ]
    
    async def get_user_teams(
        self,
        user_id: UUID,
        organization_id: UUID
    ) -> List[Dict]:
        """Get user's teams in an organization."""
        query = select(TeamMember).options(
            selectinload(TeamMember.team)
        ).join(
            Team, Team.id == TeamMember.team_id
        ).where(
            TeamMember.user_id == user_id,
            Team.organization_id == organization_id,
            TeamMember.is_active == True,
            Team.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        memberships = result.scalars().all()
        
        return [
            {
                "team_id": str(m.team_id),
                "team_name": m.team.name if m.team else None,
                "role": m.role.value,
                "joined_at": m.joined_at,
            }
            for m in memberships
        ]
    
    async def list_organization_users(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[UserListFilter] = None,
    ) -> PaginatedResponse:
        """List users in an organization with pagination."""
        # Base query
        query = select(User).join(
            UserOrganizationRole,
            UserOrganizationRole.user_id == User.id
        ).where(
            UserOrganizationRole.organization_id == organization_id
        )
        
        # Apply filters
        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        User.email.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term),
                    )
                )
            if filters.status:
                query = query.where(User.status == filters.status)
            if filters.role_id:
                query = query.where(UserOrganizationRole.role_id == filters.role_id)
            if filters.is_active is not None:
                query = query.where(UserOrganizationRole.is_active == filters.is_active)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return PaginatedResponse.create(
            items=users,
            total=total,
            page=page,
            page_size=page_size
        )
    
    async def get_organization_user(
        self,
        organization_id: UUID,
        user_id: UUID
    ) -> Optional[User]:
        """Get a user if they belong to the organization."""
        query = select(User).join(
            UserOrganizationRole,
            UserOrganizationRole.user_id == User.id
        ).where(
            User.id == user_id,
            UserOrganizationRole.organization_id == organization_id
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_invitation(
        self,
        organization_id: UUID,
        email: str,
        token_hash: str,
        expires_at: datetime,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role_id: Optional[UUID] = None,
        team_ids: Optional[List[UUID]] = None,
        invited_by_id: Optional[UUID] = None,
        message: Optional[str] = None,
    ) -> Invitation:
        """Create an invitation."""
        invitation = Invitation(
            organization_id=organization_id,
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            team_ids=team_ids,
            invited_by_id=invited_by_id,
            token_hash=token_hash,
            expires_at=expires_at,
            status=InvitationStatus.PENDING.value,
            message=message,
        )
        
        self.db.add(invitation)
        await self.db.flush()
        
        return invitation
    
    async def get_pending_invitation(
        self,
        organization_id: UUID,
        email: str
    ) -> Optional[Invitation]:
        """Get pending invitation for email in organization."""
        query = select(Invitation).where(
            Invitation.organization_id == organization_id,
            Invitation.email == email.lower(),
            Invitation.status == InvitationStatus.PENDING.value,
            Invitation.expires_at > datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def find_valid_invitation(self, token: str) -> Optional[Invitation]:
        """Find valid invitation by token."""
        # Get all pending invitations
        query = select(Invitation).where(
            Invitation.status == InvitationStatus.PENDING.value,
            Invitation.expires_at > datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        invitations = result.scalars().all()
        
        # Check each invitation's token hash
        for invitation in invitations:
            if verify_password(token, invitation.token_hash):
                return invitation
        
        return None
    
    async def add_user_to_team(
        self,
        user_id: UUID,
        team_id: UUID,
        role: str = "member"
    ) -> TeamMember:
        """Add user to a team."""
        from shared.models.team import TeamRole
        
        team_member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=TeamRole(role),
            is_active=True,
            joined_at=datetime.utcnow(),
        )
        
        self.db.add(team_member)
        await self.db.flush()
        
        return team_member
