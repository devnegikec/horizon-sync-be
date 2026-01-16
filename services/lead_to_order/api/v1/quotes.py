"""Quote management endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from shared.utils.helpers import generate_reference_number
from services.lead_to_order.models.quote import Quote, QuoteItem, QuoteStatus

router = APIRouter()


class QuoteItemCreate(BaseModel):
    product_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = None
    quantity: float = Field(default=1, gt=0)
    unit_price: float = Field(..., ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)


class QuoteCreate(BaseModel):
    deal_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_company: Optional[str] = None
    billing_address: Optional[str] = None
    valid_until: Optional[datetime] = None
    discount_percent: float = Field(default=0, ge=0, le=100)
    tax_percent: float = Field(default=0, ge=0, le=100)
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    items: List[QuoteItemCreate]


class QuoteItemResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    name: str
    description: Optional[str]
    sku: Optional[str]
    quantity: float
    unit_price: float
    discount_percent: float
    line_total: float

    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    id: UUID
    organization_id: UUID
    quote_number: str
    deal_id: Optional[UUID]
    contact_id: Optional[UUID]
    customer_name: str
    customer_email: Optional[str]
    customer_company: Optional[str]
    status: QuoteStatus
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    subtotal: float
    discount_percent: float
    discount_amount: float
    tax_percent: float
    tax_amount: float
    total: float
    currency: str
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    items: List[QuoteItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=PaginatedResponse[QuoteResponse])
async def list_quotes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[QuoteStatus] = None,
    deal_id: Optional[UUID] = None,
    contact_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("quote:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List quotes with filtering and pagination."""
    query = select(Quote).options(selectinload(Quote.items)).where(
        Quote.organization_id == tenant_id,
        Quote.deleted_at.is_(None)
    )
    
    if status:
        query = query.where(Quote.status == status)
    if deal_id:
        query = query.where(Quote.deal_id == deal_id)
    if contact_id:
        query = query.where(Quote.contact_id == contact_id)
    
    count_query = select(func.count()).select_from(
        select(Quote).where(
            Quote.organization_id == tenant_id,
            Quote.deleted_at.is_(None)
        ).subquery()
    )
    total = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Quote.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    quotes = result.scalars().unique().all()
    
    return PaginatedResponse.create(
        items=[QuoteResponse.model_validate(q) for q in quotes],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=QuoteResponse)
async def create_quote(
    quote_data: QuoteCreate,
    current_user: TokenPayload = Depends(require_permissions("quote:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new quote."""
    quote = Quote(
        organization_id=tenant_id,
        quote_number=generate_reference_number("QT"),
        deal_id=quote_data.deal_id,
        contact_id=quote_data.contact_id,
        customer_name=quote_data.customer_name,
        customer_email=quote_data.customer_email,
        customer_phone=quote_data.customer_phone,
        customer_company=quote_data.customer_company,
        billing_address=quote_data.billing_address,
        status=QuoteStatus.DRAFT,
        valid_from=datetime.utcnow(),
        valid_until=quote_data.valid_until,
        discount_percent=quote_data.discount_percent,
        tax_percent=quote_data.tax_percent,
        payment_terms=quote_data.payment_terms,
        terms_and_conditions=quote_data.terms_and_conditions,
        notes=quote_data.notes,
        created_by=UUID(current_user.sub),
    )
    
    db.add(quote)
    await db.flush()
    
    # Add items
    for i, item_data in enumerate(quote_data.items):
        item = QuoteItem(
            quote_id=quote.id,
            product_id=item_data.product_id,
            name=item_data.name,
            description=item_data.description,
            sku=item_data.sku,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent,
            sort_order=i,
        )
        item.calculate_line_total()
        item.line_total = float(item.line_total)
        db.add(item)
        quote.items.append(item)
    
    quote.calculate_totals()
    
    await db.commit()
    await db.refresh(quote)
    
    return QuoteResponse.model_validate(quote)


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("quote:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get quote details."""
    query = select(Quote).options(selectinload(Quote.items)).where(
        Quote.id == quote_id,
        Quote.organization_id == tenant_id,
        Quote.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return QuoteResponse.model_validate(quote)


@router.post("/{quote_id}/send", response_model=SuccessResponse)
async def send_quote(
    quote_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("quote:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Mark quote as sent."""
    query = select(Quote).where(
        Quote.id == quote_id,
        Quote.organization_id == tenant_id,
        Quote.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.status = QuoteStatus.SENT
    quote.sent_at = datetime.utcnow()
    
    await db.commit()
    
    # TODO: Send email to customer
    
    return SuccessResponse(message="Quote sent successfully")


@router.post("/{quote_id}/accept", response_model=SuccessResponse)
async def accept_quote(
    quote_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("quote:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Mark quote as accepted."""
    query = select(Quote).where(
        Quote.id == quote_id,
        Quote.organization_id == tenant_id,
        Quote.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.status = QuoteStatus.ACCEPTED
    quote.accepted_at = datetime.utcnow()
    
    await db.commit()
    
    return SuccessResponse(message="Quote accepted")


@router.delete("/{quote_id}", response_model=SuccessResponse)
async def delete_quote(
    quote_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("quote:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete a quote."""
    query = select(Quote).where(
        Quote.id == quote_id,
        Quote.organization_id == tenant_id,
        Quote.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Quote deleted successfully")
