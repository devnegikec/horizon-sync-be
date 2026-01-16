"""Deal management endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from services.lead_to_order.models.deal import Deal, DealStage, DealPriority

router = APIRouter()


class DealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    contact_id: Optional[UUID] = None
    company_name: Optional[str] = Field(default=None, max_length=255)
    stage: Optional[DealStage] = DealStage.PROSPECTING
    priority: Optional[DealPriority] = DealPriority.MEDIUM
    amount: Optional[float] = None
    probability: Optional[int] = Field(default=50, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class DealUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    contact_id: Optional[UUID] = None
    company_name: Optional[str] = Field(default=None, max_length=255)
    stage: Optional[DealStage] = None
    priority: Optional[DealPriority] = None
    amount: Optional[float] = None
    probability: Optional[int] = Field(default=None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class DealResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    contact_id: Optional[UUID]
    lead_id: Optional[UUID]
    company_name: Optional[str]
    stage: DealStage
    priority: DealPriority
    amount: Optional[float]
    probability: int
    expected_revenue: Optional[float]
    expected_close_date: Optional[datetime]
    actual_close_date: Optional[datetime]
    assigned_to_id: Optional[UUID]
    team_id: Optional[UUID]
    won_at: Optional[datetime]
    lost_at: Optional[datetime]
    lost_reason: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealStageUpdate(BaseModel):
    stage: DealStage
    lost_reason: Optional[str] = None
    competitor_name: Optional[str] = None


@router.get("", response_model=PaginatedResponse[DealResponse])
async def list_deals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    stage: Optional[DealStage] = None,
    priority: Optional[DealPriority] = None,
    assigned_to_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    is_open: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("deal:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List deals with filtering and pagination."""
    query = select(Deal).where(
        Deal.organization_id == tenant_id,
        Deal.deleted_at.is_(None)
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Deal.name.ilike(search_term),
                Deal.company_name.ilike(search_term),
            )
        )
    
    if stage:
        query = query.where(Deal.stage == stage)
    if priority:
        query = query.where(Deal.priority == priority)
    if assigned_to_id:
        query = query.where(Deal.assigned_to_id == assigned_to_id)
    if team_id:
        query = query.where(Deal.team_id == team_id)
    if is_open is not None:
        if is_open:
            query = query.where(Deal.stage.not_in([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]))
        else:
            query = query.where(Deal.stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Deal.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    deals = result.scalars().all()
    
    return PaginatedResponse.create(
        items=[DealResponse.model_validate(d) for d in deals],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=DealResponse)
async def create_deal(
    deal_data: DealCreate,
    current_user: TokenPayload = Depends(require_permissions("deal:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new deal."""
    deal = Deal(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **deal_data.model_dump(exclude_unset=True)
    )
    
    # Calculate expected revenue
    if deal.amount and deal.probability:
        deal.expected_revenue = deal.amount * (deal.probability / 100)
    
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    
    return DealResponse.model_validate(deal)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("deal:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get deal details."""
    query = select(Deal).where(
        Deal.id == deal_id,
        Deal.organization_id == tenant_id,
        Deal.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return DealResponse.model_validate(deal)


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID,
    update_data: DealUpdate,
    current_user: TokenPayload = Depends(require_permissions("deal:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a deal."""
    query = select(Deal).where(
        Deal.id == deal_id,
        Deal.organization_id == tenant_id,
        Deal.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(deal, key, value)
    
    # Recalculate expected revenue
    if deal.amount and deal.probability:
        deal.expected_revenue = deal.amount * (deal.probability / 100)
    
    deal.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(deal)
    
    return DealResponse.model_validate(deal)


@router.patch("/{deal_id}/stage", response_model=DealResponse)
async def update_deal_stage(
    deal_id: UUID,
    stage_data: DealStageUpdate,
    current_user: TokenPayload = Depends(require_permissions("deal:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update deal stage (move through pipeline)."""
    query = select(Deal).where(
        Deal.id == deal_id,
        Deal.organization_id == tenant_id,
        Deal.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    old_stage = deal.stage
    deal.stage = stage_data.stage
    
    # Handle won/lost
    if stage_data.stage == DealStage.CLOSED_WON:
        deal.won_at = datetime.utcnow()
        deal.actual_close_date = datetime.utcnow()
        deal.probability = 100
    elif stage_data.stage == DealStage.CLOSED_LOST:
        deal.lost_at = datetime.utcnow()
        deal.actual_close_date = datetime.utcnow()
        deal.lost_reason = stage_data.lost_reason
        deal.competitor_name = stage_data.competitor_name
        deal.probability = 0
    
    # Recalculate expected revenue
    if deal.amount:
        deal.expected_revenue = deal.amount * (deal.probability / 100)
    
    deal.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(deal)
    
    return DealResponse.model_validate(deal)


@router.delete("/{deal_id}", response_model=SuccessResponse)
async def delete_deal(
    deal_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("deal:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete a deal."""
    query = select(Deal).where(
        Deal.id == deal_id,
        Deal.organization_id == tenant_id,
        Deal.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    deal.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Deal deleted successfully")
