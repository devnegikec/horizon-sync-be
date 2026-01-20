"""Organization business logic service."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.organization import Organization, OrganizationStatus, OrganizationType
from shared.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
from shared.models.role import Role, Permission, RolePermission
from shared.models.user import User, UserOrganizationRole
from shared.models.team import Team
from shared.schemas.organization import OrganizationStats
from shared.security.permissions import (
    OWNER_PERMISSIONS, ADMIN_PERMISSIONS, MANAGER_PERMISSIONS,
    MEMBER_PERMISSIONS, VIEWER_PERMISSIONS
)


class OrganizationService:
    """Service for organization operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_organization(self, org_id: UUID) -> Optional[Organization]:
        """Get organization by ID."""
        query = select(Organization).where(
            Organization.id == org_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        query = select(Organization).where(
            Organization.slug == slug
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_organization(
        self,
        name: str,
        slug: str,
        organization_type: OrganizationType = OrganizationType.SMB,
        industry: Optional[str] = None,
        **kwargs
    ) -> Organization:
        """Create a new organization."""
        organization = Organization(
            name=name,
            slug=slug,
            status=OrganizationStatus.PENDING.value,
            **kwargs
        )
        
        self.db.add(organization)
        await self.db.flush()
        
        return organization
    
    async def update_organization(
        self,
        organization: Organization,
        data: Dict[str, Any]
    ) -> Organization:
        """Update organization fields."""
        for key, value in data.items():
            if hasattr(organization, key) and value is not None:
                setattr(organization, key, value)
        
        await self.db.flush()
        return organization
    
    async def create_subscription(
        self,
        organization_id: UUID,
        plan_code: str = "free",
    ) -> Subscription:
        """Create a subscription for an organization."""
        # Get plan
        query = select(SubscriptionPlan).where(SubscriptionPlan.code == plan_code)
        result = await self.db.execute(query)
        plan = result.scalar_one_or_none()
        
        if not plan:
            # Get free plan as fallback
            query = select(SubscriptionPlan).where(SubscriptionPlan.code == PlanType.FREE.value)
            result = await self.db.execute(query)
            plan = result.scalar_one_or_none()
        
        # Create subscription
        now = datetime.utcnow()
        subscription = Subscription(
            organization_id=organization_id,
            plan_id=plan.id if plan else None,
            status=SubscriptionStatus.ACTIVE.value,
            starts_at=now,
        )
        
        self.db.add(subscription)
        await self.db.flush()
        
        return subscription
    
    async def create_default_roles(self, organization_id: UUID) -> List[Role]:
        """Create default roles for an organization."""
        roles = []
        
        role_definitions = [
            ("owner", "Owner", OWNER_PERMISSIONS, 100, True),
            ("admin", "Administrator", ADMIN_PERMISSIONS, 90, False),
            ("manager", "Manager", MANAGER_PERMISSIONS, 70, False),
            ("member", "Member", MEMBER_PERMISSIONS, 50, True),
            ("viewer", "Viewer", VIEWER_PERMISSIONS, 10, False),
        ]
        
        for code, name, permissions, level, is_default in role_definitions:
            role = Role(
                organization_id=organization_id,
                code=code,
                name=name,
                is_system=True,
                is_default=is_default,
                hierarchy_level=level,
            )
            self.db.add(role)
            await self.db.flush()
            
            # Add permissions
            for perm_code in permissions:
                # Find or create permission
                perm_query = select(Permission).where(Permission.code == perm_code)
                perm_result = await self.db.execute(perm_query)
                permission = perm_result.scalar_one_or_none()
                
                if permission:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    self.db.add(role_perm)
            
            roles.append(role)
        
        await self.db.flush()
        return roles
    
    async def get_role_permissions(self, role_id: UUID) -> List[str]:
        """Get permission codes for a role."""
        query = select(Permission.code).join(
            RolePermission,
            RolePermission.permission_id == Permission.id
        ).where(
            RolePermission.role_id == role_id
        )
        
        result = await self.db.execute(query)
        return [row for row in result.scalars().all()]
    
    async def get_organization_stats(self, org_id: UUID) -> Optional[OrganizationStats]:
        """Get organization statistics."""
        # Get organization
        org = await self.get_organization(org_id)
        if not org:
            return None
        
        # Count users
        user_query = select(func.count()).select_from(User).where(
            User.organization_id == org_id
        )
        total_users = (await self.db.execute(user_query)).scalar() or 0
        
        active_user_query = select(func.count()).select_from(User).where(
            User.organization_id == org_id,
            User.is_active == True
        )
        active_users = (await self.db.execute(active_user_query)).scalar() or 0
        
        # Count teams
        team_query = select(func.count()).select_from(Team).where(
            Team.organization_id == org_id
        )
        total_teams = (await self.db.execute(team_query)).scalar() or 0
        
        # Get subscription info
        sub_query = select(Subscription).options(
            selectinload(Subscription.plan)
        ).where(
            Subscription.organization_id == org_id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value])
        )
        sub_result = await self.db.execute(sub_query)
        subscription = sub_result.scalar_one_or_none()
        
        plan_name = "Free"
        plan_limits = {}
        usage_percentage = {}
        
        if subscription and subscription.plan:
            plan = subscription.plan
            plan_name = plan.name
            plan_limits = {
                "max_users": plan.max_users,
                "max_teams": plan.max_teams,
            }
            usage_percentage = {
                "users": (active_users / plan.max_users * 100) if plan.max_users > 0 else 0,
                "teams": (total_teams / plan.max_teams * 100) if plan.max_teams > 0 else 0,
            }
        
        return OrganizationStats(
            total_users=total_users,
            active_users=active_users,
            total_teams=total_teams,
            total_leads=0,
            total_contacts=0,
            total_deals=0,
            total_tickets=0,
            storage_used_mb=0,
            plan_name=plan_name,
            plan_limits=plan_limits,
            usage_percentage=usage_percentage,
        )
    
    async def update_organization_settings(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Update organization settings."""
        org = await self.get_organization(org_id)
        if org:
            if org.settings is None:
                org.settings = {}
            org.settings.update(data)
            await self.db.flush()
