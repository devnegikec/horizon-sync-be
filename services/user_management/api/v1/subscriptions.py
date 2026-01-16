"""Subscription management endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.models.subscription import SubscriptionPlan, Subscription, SubscriptionStatus
from shared.schemas.organization import SubscriptionUpdateRequest
from shared.schemas.common import SuccessResponse
from shared.security.jwt import TokenPayload
from services.user_management.services.subscription_service import SubscriptionService

router = APIRouter()


class SubscriptionPlanResponse:
    """Response for subscription plan."""
    pass


@router.get("/plans")
async def list_subscription_plans(
    db: AsyncSession = Depends(get_async_session)
):
    """List all available subscription plans."""
    subscription_service = SubscriptionService(db)
    
    plans = await subscription_service.list_plans()
    
    return [
        {
            "id": str(plan.id),
            "name": plan.name,
            "code": plan.code,
            "description": plan.description,
            "plan_type": plan.plan_type.value,
            "price_monthly": float(plan.price_monthly) if plan.price_monthly else None,
            "price_yearly": float(plan.price_yearly) if plan.price_yearly else None,
            "currency": plan.currency,
            "max_users": plan.max_users,
            "max_teams": plan.max_teams,
            "max_leads": plan.max_leads,
            "max_contacts": plan.max_contacts,
            "max_deals": plan.max_deals,
            "max_tickets": plan.max_tickets,
            "max_products": plan.max_products,
            "max_storage_gb": plan.max_storage_gb,
            "features": plan.features,
            "trial_days": plan.trial_days,
        }
        for plan in plans
    ]


@router.get("/current")
async def get_current_subscription(
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current organization's subscription."""
    subscription_service = SubscriptionService(db)
    
    subscription = await subscription_service.get_active_subscription(tenant_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    plan = subscription.plan
    
    return {
        "id": str(subscription.id),
        "status": subscription.status.value,
        "plan": {
            "id": str(plan.id),
            "name": plan.name,
            "code": plan.code,
            "plan_type": plan.plan_type.value,
        },
        "billing_cycle": subscription.billing_cycle.value,
        "trial_starts_at": subscription.trial_starts_at.isoformat() if subscription.trial_starts_at else None,
        "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
        "starts_at": subscription.starts_at.isoformat() if subscription.starts_at else None,
        "ends_at": subscription.ends_at.isoformat() if subscription.ends_at else None,
        "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
        "current_usage": {
            "users": subscription.current_users,
            "teams": subscription.current_teams,
            "storage_mb": subscription.current_storage_mb,
        },
        "limits": {
            "max_users": plan.max_users,
            "max_teams": plan.max_teams,
            "max_leads": plan.max_leads,
            "max_contacts": plan.max_contacts,
            "max_deals": plan.max_deals,
            "max_tickets": plan.max_tickets,
            "max_products": plan.max_products,
            "max_storage_gb": plan.max_storage_gb,
        },
        "features": plan.features,
    }


@router.get("/usage")
async def get_subscription_usage(
    current_user: TokenPayload = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current subscription usage vs limits."""
    subscription_service = SubscriptionService(db)
    
    usage = await subscription_service.get_usage_summary(tenant_id)
    
    return usage


@router.post("/upgrade", response_model=SuccessResponse)
async def upgrade_subscription(
    upgrade_data: SubscriptionUpdateRequest,
    current_user: TokenPayload = Depends(require_permissions("subscription:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Upgrade subscription to a higher plan."""
    subscription_service = SubscriptionService(db)
    
    # Get target plan
    target_plan = await subscription_service.get_plan_by_code(upgrade_data.plan_code)
    if not target_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Get current subscription
    current_sub = await subscription_service.get_active_subscription(tenant_id)
    if not current_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to upgrade"
        )
    
    # Validate upgrade (can't downgrade through this endpoint)
    if target_plan.hierarchy_level <= current_sub.plan.hierarchy_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /downgrade endpoint for downgrading"
        )
    
    # Perform upgrade
    await subscription_service.upgrade_subscription(
        subscription=current_sub,
        new_plan=target_plan,
        billing_cycle=upgrade_data.billing_cycle,
    )
    
    await db.commit()
    
    return SuccessResponse(message=f"Subscription upgraded to {target_plan.name}")


@router.post("/downgrade", response_model=SuccessResponse)
async def downgrade_subscription(
    downgrade_data: SubscriptionUpdateRequest,
    current_user: TokenPayload = Depends(require_permissions("subscription:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Downgrade subscription to a lower plan."""
    subscription_service = SubscriptionService(db)
    
    # Get target plan
    target_plan = await subscription_service.get_plan_by_code(downgrade_data.plan_code)
    if not target_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Get current subscription
    current_sub = await subscription_service.get_active_subscription(tenant_id)
    if not current_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to downgrade"
        )
    
    # Check if downgrade is valid (usage must be within new limits)
    validation = await subscription_service.validate_downgrade(
        tenant_id, target_plan
    )
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot downgrade: {', '.join(validation['issues'])}"
        )
    
    # Schedule downgrade (takes effect at end of billing period)
    await subscription_service.schedule_downgrade(
        subscription=current_sub,
        new_plan=target_plan,
    )
    
    await db.commit()
    
    return SuccessResponse(
        message=f"Subscription will be downgraded to {target_plan.name} at the end of the current billing period"
    )


@router.post("/cancel", response_model=SuccessResponse)
async def cancel_subscription(
    current_user: TokenPayload = Depends(require_permissions("subscription:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Cancel subscription (will be downgraded to free plan)."""
    subscription_service = SubscriptionService(db)
    
    # Get current subscription
    current_sub = await subscription_service.get_active_subscription(tenant_id)
    if not current_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )
    
    # Cancel subscription
    await subscription_service.cancel_subscription(current_sub)
    
    await db.commit()
    
    return SuccessResponse(
        message="Subscription cancelled. Access will continue until the end of the billing period."
    )
