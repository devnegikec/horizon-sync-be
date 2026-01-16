"""Lead management endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_session
from shared.middleware.auth import get_current_user, require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from services.lead_to_order.models.lead import Lead, LeadStatus, LeadSource, LeadPriority

router = APIRouter()


# Pydantic schemas
class LeadCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=100)
    source: Optional[LeadSource] = LeadSource.OTHER
    priority: Optional[LeadPriority] = LeadPriority.MEDIUM
    estimated_value: Optional[float] = None
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class LeadUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=100)
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    priority: Optional[LeadPriority] = None
    estimated_value: Optional[float] = None
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    next_follow_up: Optional[datetime] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class LeadResponse(BaseModel):
    id: UUID
    organization_id: UUID
    title: str
    description: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    company_name: Optional[str]
    job_title: Optional[str]
    status: LeadStatus
    source: LeadSource
    priority: LeadPriority
    score: int
    estimated_value: Optional[float]
    assigned_to_id: Optional[UUID]
    team_id: Optional[UUID]
    next_follow_up: Optional[datetime]
    last_contacted_at: Optional[datetime]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadConvert(BaseModel):
    create_contact: bool = True
    create_deal: bool = True
    deal_name: Optional[str] = None
    deal_amount: Optional[float] = None


@router.get("", response_model=PaginatedResponse[LeadResponse])
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    priority: Optional[LeadPriority] = None,
    assigned_to_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("lead:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List leads with filtering and pagination."""
    query = select(Lead).where(
        Lead.organization_id == tenant_id,
        Lead.deleted_at.is_(None)
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Lead.title.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.company_name.ilike(search_term),
                Lead.first_name.ilike(search_term),
                Lead.last_name.ilike(search_term),
            )
        )
    
    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    if priority:
        query = query.where(Lead.priority == priority)
    if assigned_to_id:
        query = query.where(Lead.assigned_to_id == assigned_to_id)
    if team_id:
        query = query.where(Lead.team_id == team_id)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Lead.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return PaginatedResponse.create(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: TokenPayload = Depends(require_permissions("lead:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new lead."""
    lead = Lead(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **lead_data.model_dump(exclude_unset=True)
    )
    
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("lead:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get lead details."""
    query = select(Lead).where(
        Lead.id == lead_id,
        Lead.organization_id == tenant_id,
        Lead.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    update_data: LeadUpdate,
    current_user: TokenPayload = Depends(require_permissions("lead:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a lead."""
    query = select(Lead).where(
        Lead.id == lead_id,
        Lead.organization_id == tenant_id,
        Lead.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    
    lead.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(lead)
    
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", response_model=SuccessResponse)
async def delete_lead(
    lead_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("lead:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete a lead."""
    query = select(Lead).where(
        Lead.id == lead_id,
        Lead.organization_id == tenant_id,
        Lead.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Lead deleted successfully")


@router.post("/{lead_id}/convert", response_model=dict)
async def convert_lead(
    lead_id: UUID,
    convert_data: LeadConvert,
    current_user: TokenPayload = Depends(require_permissions("lead:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Convert a lead to contact and/or deal."""
    from services.lead_to_order.models.contact import Contact
    from services.lead_to_order.models.deal import Deal, DealStage
    
    query = select(Lead).where(
        Lead.id == lead_id,
        Lead.organization_id == tenant_id,
        Lead.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status == LeadStatus.WON:
        raise HTTPException(status_code=400, detail="Lead already converted")
    
    contact_id = None
    deal_id = None
    
    # Create contact
    if convert_data.create_contact:
        contact = Contact(
            organization_id=tenant_id,
            first_name=lead.first_name or "Unknown",
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            company_name=lead.company_name,
            job_title=lead.job_title,
            source_lead_id=lead.id,
            assigned_to_id=lead.assigned_to_id,
            created_by=UUID(current_user.sub),
        )
        db.add(contact)
        await db.flush()
        contact_id = contact.id
    
    # Create deal
    if convert_data.create_deal:
        deal = Deal(
            organization_id=tenant_id,
            name=convert_data.deal_name or f"Deal - {lead.title}",
            lead_id=lead.id,
            contact_id=contact_id,
            company_name=lead.company_name,
            stage=DealStage.QUALIFICATION,
            amount=convert_data.deal_amount or lead.estimated_value,
            assigned_to_id=lead.assigned_to_id,
            team_id=lead.team_id,
            created_by=UUID(current_user.sub),
        )
        db.add(deal)
        await db.flush()
        deal_id = deal.id
    
    # Update lead
    lead.status = LeadStatus.WON
    lead.converted_at = datetime.utcnow()
    lead.converted_to_contact_id = contact_id
    lead.converted_to_deal_id = deal_id
    
    await db.commit()
    
    return {
        "message": "Lead converted successfully",
        "contact_id": str(contact_id) if contact_id else None,
        "deal_id": str(deal_id) if deal_id else None,
    }
