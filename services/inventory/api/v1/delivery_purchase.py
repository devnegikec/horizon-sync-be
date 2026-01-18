"""Delivery Note, Purchase Receipt, and Landed Cost Voucher endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from services.inventory.models.transactions import (
    DeliveryNote, DeliveryNoteItem, PurchaseReceipt, PurchaseReceiptItem,
    LandedCostVoucher, LandedCostPurchaseReceipt, LandedCostItem,
    LandedCostTaxesAndCharges, DocumentStatus
)


router = APIRouter()


# ==================== Delivery Note Schemas ====================
class DeliveryNoteItemCreate(BaseModel):
    item_id: UUID
    item_name: Optional[str] = None
    description: Optional[str] = None
    warehouse_id: UUID
    qty: float = Field(..., gt=0)
    uom: str
    rate: Optional[float] = None
    sales_order_item_id: Optional[UUID] = None
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None
    quality_inspection_id: Optional[UUID] = None


class DeliveryNoteCreate(BaseModel):
    customer_id: UUID
    customer_name: Optional[str] = None
    sales_order_id: Optional[UUID] = None
    pick_list_id: Optional[UUID] = None
    posting_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    warehouse_id: UUID
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    over_delivery_percentage: float = Field(default=0, ge=0, le=100)
    remarks: Optional[str] = None
    items: List[DeliveryNoteItemCreate]


class DeliveryNoteUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    delivery_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    remarks: Optional[str] = None


class DeliveryNoteItemResponse(BaseModel):
    id: UUID
    delivery_note_id: UUID
    item_id: UUID
    item_name: Optional[str]
    description: Optional[str]
    warehouse_id: UUID
    qty: float
    uom: str
    rate: Optional[float]
    amount: Optional[float]
    sales_order_item_id: Optional[UUID]
    batch_no: Optional[str]
    serial_nos: List[str]
    quality_inspection_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryNoteResponse(BaseModel):
    id: UUID
    organization_id: UUID
    delivery_note_no: str
    customer_id: UUID
    customer_name: Optional[str]
    sales_order_id: Optional[UUID]
    pick_list_id: Optional[UUID]
    posting_date: datetime
    delivery_date: Optional[datetime]
    warehouse_id: UUID
    status: DocumentStatus
    shipping_address_line1: Optional[str]
    shipping_city: Optional[str]
    shipping_state: Optional[str]
    shipping_country: Optional[str]
    tracking_number: Optional[str]
    carrier: Optional[str]
    total_qty: float
    total_amount: float
    over_delivery_percentage: float
    sales_invoice_id: Optional[UUID]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DeliveryNoteDetailResponse(DeliveryNoteResponse):
    items: List[DeliveryNoteItemResponse]


# ==================== Purchase Receipt Schemas ====================
class PurchaseReceiptItemCreate(BaseModel):
    item_id: UUID
    item_name: Optional[str] = None
    description: Optional[str] = None
    warehouse_id: UUID
    qty: float = Field(..., gt=0)
    received_qty: Optional[float] = None
    uom: str
    rate: Optional[float] = None
    purchase_order_item_id: Optional[UUID] = None
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None
    quality_inspection_id: Optional[UUID] = None


class PurchaseReceiptCreate(BaseModel):
    supplier_id: UUID
    supplier_name: Optional[str] = None
    purchase_order_id: Optional[UUID] = None
    posting_date: Optional[datetime] = None
    warehouse_id: UUID
    supplier_delivery_note: Optional[str] = None
    supplier_invoice_no: Optional[str] = None
    over_receipt_percentage: float = Field(default=0, ge=0, le=100)
    apply_putaway_rule: bool = False
    remarks: Optional[str] = None
    items: List[PurchaseReceiptItemCreate]


class PurchaseReceiptUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    supplier_delivery_note: Optional[str] = None
    supplier_invoice_no: Optional[str] = None
    remarks: Optional[str] = None


class PurchaseReceiptItemResponse(BaseModel):
    id: UUID
    purchase_receipt_id: UUID
    item_id: UUID
    item_name: Optional[str]
    description: Optional[str]
    warehouse_id: UUID
    qty: float
    received_qty: Optional[float]
    uom: str
    rate: Optional[float]
    amount: Optional[float]
    purchase_order_item_id: Optional[UUID]
    batch_no: Optional[str]
    serial_nos: List[str]
    quality_inspection_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseReceiptResponse(BaseModel):
    id: UUID
    organization_id: UUID
    purchase_receipt_no: str
    supplier_id: UUID
    supplier_name: Optional[str]
    purchase_order_id: Optional[UUID]
    posting_date: datetime
    warehouse_id: UUID
    status: DocumentStatus
    supplier_delivery_note: Optional[str]
    supplier_invoice_no: Optional[str]
    total_qty: float
    total_amount: float
    over_receipt_percentage: float
    apply_putaway_rule: bool
    purchase_invoice_id: Optional[UUID]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PurchaseReceiptDetailResponse(PurchaseReceiptResponse):
    items: List[PurchaseReceiptItemResponse]


# ==================== Landed Cost Voucher Schemas ====================
class LandedCostTaxesAndChargesCreate(BaseModel):
    expense_account_id: UUID
    description: Optional[str] = None
    amount: float = Field(..., gt=0)


class LandedCostVoucherCreate(BaseModel):
    posting_date: Optional[datetime] = None
    distribute_charges_based_on: str = Field(default="qty")
    purchase_receipt_ids: List[UUID]
    taxes_and_charges: List[LandedCostTaxesAndChargesCreate]
    remarks: Optional[str] = None


class LandedCostVoucherUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    remarks: Optional[str] = None


class LandedCostVoucherResponse(BaseModel):
    id: UUID
    organization_id: UUID
    voucher_no: str
    posting_date: datetime
    status: DocumentStatus
    distribute_charges_based_on: str
    total_landed_cost: float
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== Delivery Note Endpoints ====================
@router.get("/delivery-notes", response_model=PaginatedResponse[DeliveryNoteResponse])
async def list_delivery_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[DocumentStatus] = None,
    customer_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:delivery_note:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all delivery notes with pagination and filters."""
    query = select(DeliveryNote).where(
        DeliveryNote.organization_id == tenant_id
    )
    
    if status:
        query = query.where(DeliveryNote.status == status)
    
    if customer_id:
        query = query.where(DeliveryNote.customer_id == customer_id)
    
    if from_date:
        query = query.where(DeliveryNote.posting_date >= from_date)
    
    if to_date:
        query = query.where(DeliveryNote.posting_date <= to_date)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    delivery_notes = (await db.execute(
        query.order_by(DeliveryNote.posting_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [DeliveryNoteResponse.model_validate(dn) for dn in delivery_notes],
        total, page, page_size
    )


@router.post("/delivery-notes", response_model=DeliveryNoteDetailResponse)
async def create_delivery_note(
    data: DeliveryNoteCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:delivery_note:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new delivery note."""
    # Generate delivery note number
    count = (await db.execute(
        select(func.count()).select_from(DeliveryNote).where(
            DeliveryNote.organization_id == tenant_id
        )
    )).scalar() or 0
    delivery_note_no = f"DN-{count + 1:06d}"
    
    # Calculate totals
    total_qty = sum(item.qty for item in data.items)
    total_amount = sum((item.qty * (item.rate or 0)) for item in data.items)
    
    # Create delivery note
    delivery_note = DeliveryNote(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        delivery_note_no=delivery_note_no,
        total_qty=total_qty,
        total_amount=total_amount,
        posting_date=data.posting_date or datetime.utcnow(),
        **data.model_dump(exclude={"items"}, exclude_unset=True)
    )
    
    db.add(delivery_note)
    await db.flush()
    
    # Create delivery note items
    for item_data in data.items:
        amount = (item_data.qty * item_data.rate) if item_data.rate else None
        
        item = DeliveryNoteItem(
            organization_id=tenant_id,
            delivery_note_id=delivery_note.id,
            amount=amount,
            **item_data.model_dump(exclude_unset=True)
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(delivery_note)
    
    # Fetch items for response
    items = (await db.execute(
        select(DeliveryNoteItem).where(DeliveryNoteItem.delivery_note_id == delivery_note.id)
    )).scalars().all()
    
    response = DeliveryNoteDetailResponse.model_validate(delivery_note)
    response.items = [DeliveryNoteItemResponse.model_validate(i) for i in items]
    
    return response


@router.get("/delivery-notes/{delivery_note_id}", response_model=DeliveryNoteDetailResponse)
async def get_delivery_note(
    delivery_note_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:delivery_note:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get delivery note by ID with items."""
    delivery_note = (await db.execute(
        select(DeliveryNote).where(
            DeliveryNote.id == delivery_note_id,
            DeliveryNote.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not delivery_note:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    
    items = (await db.execute(
        select(DeliveryNoteItem).where(DeliveryNoteItem.delivery_note_id == delivery_note_id)
    )).scalars().all()
    
    response = DeliveryNoteDetailResponse.model_validate(delivery_note)
    response.items = [DeliveryNoteItemResponse.model_validate(i) for i in items]
    
    return response


@router.patch("/delivery-notes/{delivery_note_id}", response_model=DeliveryNoteResponse)
async def update_delivery_note(
    delivery_note_id: UUID,
    data: DeliveryNoteUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:delivery_note:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update delivery note."""
    delivery_note = (await db.execute(
        select(DeliveryNote).where(
            DeliveryNote.id == delivery_note_id,
            DeliveryNote.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not delivery_note:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(delivery_note, key, value)
    
    if data.status == DocumentStatus.SUBMITTED:
        delivery_note.submitted_at = datetime.utcnow()
    elif data.status == DocumentStatus.CANCELLED:
        delivery_note.cancelled_at = datetime.utcnow()
    
    delivery_note.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(delivery_note)
    
    return DeliveryNoteResponse.model_validate(delivery_note)


# ==================== Purchase Receipt Endpoints ====================
@router.get("/purchase-receipts", response_model=PaginatedResponse[PurchaseReceiptResponse])
async def list_purchase_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[DocumentStatus] = None,
    supplier_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:purchase_receipt:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all purchase receipts with pagination and filters."""
    query = select(PurchaseReceipt).where(
        PurchaseReceipt.organization_id == tenant_id
    )
    
    if status:
        query = query.where(PurchaseReceipt.status == status)
    
    if supplier_id:
        query = query.where(PurchaseReceipt.supplier_id == supplier_id)
    
    if from_date:
        query = query.where(PurchaseReceipt.posting_date >= from_date)
    
    if to_date:
        query = query.where(PurchaseReceipt.posting_date <= to_date)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    receipts = (await db.execute(
        query.order_by(PurchaseReceipt.posting_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [PurchaseReceiptResponse.model_validate(pr) for pr in receipts],
        total, page, page_size
    )


@router.post("/purchase-receipts", response_model=PurchaseReceiptDetailResponse)
async def create_purchase_receipt(
    data: PurchaseReceiptCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:purchase_receipt:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new purchase receipt."""
    # Generate purchase receipt number
    count = (await db.execute(
        select(func.count()).select_from(PurchaseReceipt).where(
            PurchaseReceipt.organization_id == tenant_id
        )
    )).scalar() or 0
    purchase_receipt_no = f"PR-{count + 1:06d}"
    
    # Calculate totals
    total_qty = sum(item.qty for item in data.items)
    total_amount = sum((item.qty * (item.rate or 0)) for item in data.items)
    
    # Create purchase receipt
    receipt = PurchaseReceipt(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        purchase_receipt_no=purchase_receipt_no,
        total_qty=total_qty,
        total_amount=total_amount,
        posting_date=data.posting_date or datetime.utcnow(),
        **data.model_dump(exclude={"items"}, exclude_unset=True)
    )
    
    db.add(receipt)
    await db.flush()
    
    # Create purchase receipt items
    for item_data in data.items:
        amount = (item_data.qty * item_data.rate) if item_data.rate else None
        
        item = PurchaseReceiptItem(
            organization_id=tenant_id,
            purchase_receipt_id=receipt.id,
            amount=amount,
            **item_data.model_dump(exclude_unset=True)
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(receipt)
    
    # Fetch items for response
    items = (await db.execute(
        select(PurchaseReceiptItem).where(PurchaseReceiptItem.purchase_receipt_id == receipt.id)
    )).scalars().all()
    
    response = PurchaseReceiptDetailResponse.model_validate(receipt)
    response.items = [PurchaseReceiptItemResponse.model_validate(i) for i in items]
    
    return response


@router.get("/purchase-receipts/{receipt_id}", response_model=PurchaseReceiptDetailResponse)
async def get_purchase_receipt(
    receipt_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:purchase_receipt:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get purchase receipt by ID with items."""
    receipt = (await db.execute(
        select(PurchaseReceipt).where(
            PurchaseReceipt.id == receipt_id,
            PurchaseReceipt.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Purchase receipt not found")
    
    items = (await db.execute(
        select(PurchaseReceiptItem).where(PurchaseReceiptItem.purchase_receipt_id == receipt_id)
    )).scalars().all()
    
    response = PurchaseReceiptDetailResponse.model_validate(receipt)
    response.items = [PurchaseReceiptItemResponse.model_validate(i) for i in items]
    
    return response


@router.patch("/purchase-receipts/{receipt_id}", response_model=PurchaseReceiptResponse)
async def update_purchase_receipt(
    receipt_id: UUID,
    data: PurchaseReceiptUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:purchase_receipt:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update purchase receipt."""
    receipt = (await db.execute(
        select(PurchaseReceipt).where(
            PurchaseReceipt.id == receipt_id,
            PurchaseReceipt.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Purchase receipt not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(receipt, key, value)
    
    if data.status == DocumentStatus.SUBMITTED:
        receipt.submitted_at = datetime.utcnow()
    elif data.status == DocumentStatus.CANCELLED:
        receipt.cancelled_at = datetime.utcnow()
    
    receipt.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(receipt)
    
    return PurchaseReceiptResponse.model_validate(receipt)


# ==================== Landed Cost Voucher Endpoints ====================
@router.post("/landed-cost-vouchers", response_model=LandedCostVoucherResponse)
async def create_landed_cost_voucher(
    data: LandedCostVoucherCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:landed_cost:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new landed cost voucher."""
    # Generate voucher number
    count = (await db.execute(
        select(func.count()).select_from(LandedCostVoucher).where(
            LandedCostVoucher.organization_id == tenant_id
        )
    )).scalar() or 0
    voucher_no = f"LCV-{count + 1:06d}"
    
    # Calculate total landed cost
    total_landed_cost = sum(charge.amount for charge in data.taxes_and_charges)
    
    # Create voucher
    voucher = LandedCostVoucher(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        voucher_no=voucher_no,
        total_landed_cost=total_landed_cost,
        posting_date=data.posting_date or datetime.utcnow(),
        **data.model_dump(exclude={"purchase_receipt_ids", "taxes_and_charges"}, exclude_unset=True)
    )
    
    db.add(voucher)
    await db.flush()
    
    # Link purchase receipts
    for pr_id in data.purchase_receipt_ids:
        # Fetch purchase receipt to get grand total
        pr = (await db.execute(
            select(PurchaseReceipt).where(
                PurchaseReceipt.id == pr_id,
                PurchaseReceipt.organization_id == tenant_id
            )
        )).scalar_one_or_none()
        
        if not pr:
            raise HTTPException(status_code=404, detail=f"Purchase receipt {pr_id} not found")
        
        link = LandedCostPurchaseReceipt(
            organization_id=tenant_id,
            landed_cost_voucher_id=voucher.id,
            purchase_receipt_id=pr_id,
            grand_total=pr.total_amount
        )
        db.add(link)
    
    # Add taxes and charges
    for charge_data in data.taxes_and_charges:
        charge = LandedCostTaxesAndCharges(
            organization_id=tenant_id,
            landed_cost_voucher_id=voucher.id,
            **charge_data.model_dump()
        )
        db.add(charge)
    
    # TODO: Distribute charges to items based on distribute_charges_based_on
    
    await db.commit()
    await db.refresh(voucher)
    
    return LandedCostVoucherResponse.model_validate(voucher)
