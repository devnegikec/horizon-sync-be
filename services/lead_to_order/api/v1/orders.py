"""Order management endpoints."""
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
from services.lead_to_order.models.order import Order, OrderItem, OrderStatus, PaymentStatus

router = APIRouter()


class OrderItemCreate(BaseModel):
    product_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = None
    quantity: float = Field(default=1, gt=0)
    unit_price: float = Field(..., ge=0)
    discount_amount: float = Field(default=0, ge=0)


class OrderCreate(BaseModel):
    quote_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_company: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    discount_amount: float = Field(default=0, ge=0)
    tax_amount: float = Field(default=0, ge=0)
    shipping_amount: float = Field(default=0, ge=0)
    payment_method: Optional[str] = None
    payment_due_date: Optional[datetime] = None
    shipping_method: Optional[str] = None
    customer_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    name: str
    description: Optional[str]
    sku: Optional[str]
    quantity: float
    unit_price: float
    discount_amount: float
    line_total: float
    quantity_shipped: float
    quantity_delivered: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: UUID
    organization_id: UUID
    order_number: str
    quote_id: Optional[UUID]
    deal_id: Optional[UUID]
    contact_id: Optional[UUID]
    customer_name: str
    customer_email: Optional[str]
    customer_company: Optional[str]
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: float
    discount_amount: float
    tax_amount: float
    shipping_amount: float
    total: float
    amount_paid: float
    amount_due: float
    currency: str
    tracking_number: Optional[str]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    cancellation_reason: Optional[str] = None


class PaymentRecord(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    payment_status: Optional[PaymentStatus] = None,
    contact_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("order:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List orders with filtering and pagination."""
    query = select(Order).options(selectinload(Order.items)).where(
        Order.organization_id == tenant_id,
        Order.deleted_at.is_(None)
    )
    
    if status:
        query = query.where(Order.status == status)
    if payment_status:
        query = query.where(Order.payment_status == payment_status)
    if contact_id:
        query = query.where(Order.contact_id == contact_id)
    
    count_query = select(func.count()).select_from(
        select(Order).where(
            Order.organization_id == tenant_id,
            Order.deleted_at.is_(None)
        ).subquery()
    )
    total = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Order.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    orders = result.scalars().unique().all()
    
    return PaginatedResponse.create(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: TokenPayload = Depends(require_permissions("order:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new order."""
    order = Order(
        organization_id=tenant_id,
        order_number=generate_reference_number("ORD"),
        quote_id=order_data.quote_id,
        deal_id=order_data.deal_id,
        contact_id=order_data.contact_id,
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        customer_company=order_data.customer_company,
        billing_address=order_data.billing_address,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        discount_amount=order_data.discount_amount,
        tax_amount=order_data.tax_amount,
        shipping_amount=order_data.shipping_amount,
        payment_method=order_data.payment_method,
        payment_due_date=order_data.payment_due_date,
        shipping_method=order_data.shipping_method,
        customer_notes=order_data.customer_notes,
        internal_notes=order_data.internal_notes,
        created_by=UUID(current_user.sub),
    )
    
    db.add(order)
    await db.flush()
    
    # Add items
    for i, item_data in enumerate(order_data.items):
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            name=item_data.name,
            description=item_data.description,
            sku=item_data.sku,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_amount=item_data.discount_amount,
            sort_order=i,
        )
        item.calculate_line_total()
        item.line_total = float(item.line_total)
        db.add(item)
        order.items.append(item)
    
    order.calculate_totals()
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("order:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get order details."""
    query = select(Order).options(selectinload(Order.items)).where(
        Order.id == order_id,
        Order.organization_id == tenant_id,
        Order.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_data: OrderStatusUpdate,
    current_user: TokenPayload = Depends(require_permissions("order:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update order status."""
    query = select(Order).options(selectinload(Order.items)).where(
        Order.id == order_id,
        Order.organization_id == tenant_id,
        Order.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_data.status
    
    if status_data.status == OrderStatus.CONFIRMED:
        order.confirmed_at = datetime.utcnow()
    elif status_data.status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
        if status_data.tracking_number:
            order.tracking_number = status_data.tracking_number
    elif status_data.status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()
    elif status_data.status == OrderStatus.COMPLETED:
        order.completed_at = datetime.utcnow()
    elif status_data.status == OrderStatus.CANCELLED:
        order.cancelled_at = datetime.utcnow()
        order.cancellation_reason = status_data.cancellation_reason
    
    order.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/payment", response_model=OrderResponse)
async def record_payment(
    order_id: UUID,
    payment_data: PaymentRecord,
    current_user: TokenPayload = Depends(require_permissions("order:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Record a payment for an order."""
    query = select(Order).options(selectinload(Order.items)).where(
        Order.id == order_id,
        Order.organization_id == tenant_id,
        Order.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.amount_paid = float(order.amount_paid or 0) + payment_data.amount
    order.amount_due = float(order.total) - float(order.amount_paid)
    
    if payment_data.payment_method:
        order.payment_method = payment_data.payment_method
    if payment_data.payment_reference:
        order.payment_reference = payment_data.payment_reference
    
    # Update payment status
    if order.amount_due <= 0:
        order.payment_status = PaymentStatus.PAID
    elif order.amount_paid > 0:
        order.payment_status = PaymentStatus.PARTIAL
    
    order.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", response_model=SuccessResponse)
async def delete_order(
    order_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("order:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete an order."""
    query = select(Order).where(
        Order.id == order_id,
        Order.organization_id == tenant_id,
        Order.deleted_at.is_(None)
    )
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Order deleted successfully")
