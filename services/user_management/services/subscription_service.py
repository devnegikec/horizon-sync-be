"""Subscription business logic service."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models.subscription import (
    Subscription, SubscriptionPlan, SubscriptionStatus,
    BillingCycle, PlanType
)
from shared.models.user import User
from shared.models.team import Team


class SubscriptionService:
    """Service for subscription operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_plans(self, is_public: bool = True) -> List[SubscriptionPlan]:
        """List available subscription plans."""
        query = select(SubscriptionPlan).where(
            SubscriptionPlan.is_active == True
        )
        
        if is_public:
            query = query.where(SubscriptionPlan.is_public == True)
        
        query = query.order_by(SubscriptionPlan.sort_order)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_plan_by_code(self, code: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by code."""
        query = select(SubscriptionPlan).where(
            SubscriptionPlan.code == code,
            SubscriptionPlan.is_active == True
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_subscription(
        self,
        organization_id: UUID
    ) -> Optional[Subscription]:
        """Get active subscription for organization."""
        query = select(Subscription).options(
            selectinload(Subscription.plan)
        ).where(
            Subscription.organization_id == organization_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ])
        ).order_by(Subscription.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_usage_summary(self, organization_id: UUID) -> Dict[str, Any]:
        """Get current usage vs limits."""
        subscription = await self.get_active_subscription(organization_id)
        
        if not subscription or not subscription.plan:
            return {"error": "No active subscription"}
        
        plan = subscription.plan
        
        # Count current usage
        user_count = await self._count_users(organization_id)
        team_count = await self._count_teams(organization_id)
        
        return {
            "plan_name": plan.name,
            "plan_code": plan.code,
            "usage": {
                "users": {
                    "current": user_count,
                    "limit": plan.max_users,
                    "percentage": round(user_count / plan.max_users * 100, 1) if plan.max_users > 0 else 0,
                },
                "teams": {
                    "current": team_count,
                    "limit": plan.max_teams,
                    "percentage": round(team_count / plan.max_teams * 100, 1) if plan.max_teams > 0 else 0,
                },
                "storage": {
                    "current_mb": float(subscription.current_storage_mb or 0),
                    "limit_gb": plan.max_storage_gb,
                    "percentage": round(float(subscription.current_storage_mb or 0) / (plan.max_storage_gb * 1024) * 100, 1) if plan.max_storage_gb > 0 else 0,
                },
            },
            "limits": {
                "max_leads": plan.max_leads,
                "max_contacts": plan.max_contacts,
                "max_deals": plan.max_deals,
                "max_tickets": plan.max_tickets,
                "max_products": plan.max_products,
                "max_api_calls_per_day": plan.max_api_calls_per_day,
            },
            "features": plan.features,
        }
    
    async def _count_users(self, organization_id: UUID) -> int:
        """Count active users in organization."""
        query = select(func.count()).select_from(User).where(
            User.organization_id == organization_id,
            User.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_teams(self, organization_id: UUID) -> int:
        """Count active teams in organization."""
        query = select(func.count()).select_from(Team).where(
            Team.organization_id == organization_id
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def upgrade_subscription(
        self,
        subscription: Subscription,
        new_plan: SubscriptionPlan,
        billing_cycle: str = "monthly",
    ) -> Subscription:
        """Upgrade subscription to new plan."""
        subscription.plan_id = new_plan.id
        subscription.billing_cycle = BillingCycle(billing_cycle)
        subscription.status = SubscriptionStatus.ACTIVE
        
        # End trial if was in trial
        if subscription.trial_ends_at:
            subscription.trial_ends_at = datetime.utcnow()
        
        if not subscription.starts_at:
            subscription.starts_at = datetime.utcnow()
        
        await self.db.flush()
        
        return subscription
    
    async def validate_downgrade(
        self,
        organization_id: UUID,
        target_plan: SubscriptionPlan
    ) -> Dict[str, Any]:
        """Validate if downgrade is possible."""
        issues = []
        
        # Check user count
        user_count = await self._count_users(organization_id)
        if user_count > target_plan.max_users:
            issues.append(
                f"Current users ({user_count}) exceeds new plan limit ({target_plan.max_users})"
            )
        
        # Check team count
        team_count = await self._count_teams(organization_id)
        if team_count > target_plan.max_teams:
            issues.append(
                f"Current teams ({team_count}) exceeds new plan limit ({target_plan.max_teams})"
            )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
    
    async def schedule_downgrade(
        self,
        subscription: Subscription,
        new_plan: SubscriptionPlan,
    ) -> Subscription:
        """Schedule downgrade at end of billing period."""
        # Store pending change in extra_data
        subscription.extra_data = subscription.extra_data or {}
        subscription.extra_data["pending_downgrade"] = {
            "new_plan_id": str(new_plan.id),
            "scheduled_at": datetime.utcnow().isoformat(),
        }
        
        await self.db.flush()
        
        return subscription
    
    async def cancel_subscription(
        self,
        subscription: Subscription
    ) -> Subscription:
        """Cancel subscription."""
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        await self.db.flush()
        
        return subscription
