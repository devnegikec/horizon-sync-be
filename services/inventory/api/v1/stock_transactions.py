"""Stock Entry and Reconciliation endpoints."""
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
from services.inventory.models.stock_entry import (
    StockEntry, StockEntryItem, StockEntryType, StockEntryStatus,
    StockReconciliation, StockReconciliationItem
)


router = APIRouter()


# ==================== Stock Entry Schemas ====================
class StockEntryItemCreate(BaseModel):
    item_id: UUID
    source_warehouse_id: Optional[UUID] = None
    target_warehouse_id: Optional[UUID] = None
    qty: float = Field(..., gt=0)
    uom: str
    basic_rate: Optional[float] = None
    valuation_rate: Optional[float] = None
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None
    quality_inspection_id: Optional[UUID] = None
    description: Optional[str] = None


class StockEntryCreate(BaseModel):
    stock_entry_type: StockEntryType
    from_warehouse_id: Optional[UUID] = None
    to_warehouse_id: Optional[UUID] = None
    posting_date: Optional[datetime] = None
    posting_time: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    remarks: Optional[str] = None
    expense_account_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    is_backflush: bool = False
    bom_id: Optional[UUID] = None
    items: List[StockEntryItemCreate]


class StockEntryUpdate(BaseModel):
    status: Optional[StockEntryStatus] = None
    posting_date: Optional[datetime] = None
    posting_time: Optional[str] = None
    remarks: Optional[str] = None


class StockEntryItemResponse(BaseModel):
    id: UUID
    stock_entry_id: UUID
    item_id: UUID
    source_warehouse_id: Optional[UUID]
    target_warehouse_id: Optional[UUID]
    qty: float
    uom: str
    basic_rate: Optional[float]
    basic_amount: Optional[float]
    valuation_rate: Optional[float]
    batch_no: Optional[str]
    serial_nos: List[str]
    quality_inspection_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockEntryResponse(BaseModel):
    id: UUID
    organization_id: UUID
    stock_entry_no: str
    stock_entry_type: StockEntryType
    from_warehouse_id: Optional[UUID]
    to_warehouse_id: Optional[UUID]
    posting_date: datetime
    posting_time: Optional[str]
    status: StockEntryStatus
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    remarks: Optional[str]
    total_value: float
    expense_account_id: Optional[UUID]
    cost_center_id: Optional[UUID]
    is_backflush: bool
    bom_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StockEntryDetailResponse(StockEntryResponse):
    items: List[StockEntryItemResponse]


# ==================== Stock Reconciliation Schemas ====================
class StockReconciliationItemCreate(BaseModel):
    item_id: UUID
    warehouse_id: UUID
    qty: float = Field(..., ge=0)
    valuation_rate: Optional[float] = None
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None


class StockReconciliationCreate(BaseModel):
    purpose: str = Field(default="stock_reconciliation")
    posting_date: Optional[datetime] = None
    posting_time: Optional[str] = None
    expense_account_id: Optional[UUID] = None
    difference_account_id: Optional[UUID] = None
    remarks: Optional[str] = None
    items: List[StockReconciliationItemCreate]


class StockReconciliationUpdate(BaseModel):
    status: Optional[StockEntryStatus] = None
    posting_date: Optional[datetime] = None
    posting_time: Optional[str] = None
    remarks: Optional[str] = None


class StockReconciliationItemResponse(BaseModel):
    id: UUID
    reconciliation_id: UUID
    item_id: UUID
    warehouse_id: UUID
    current_qty: float
    qty: float
    qty_difference: float
    current_valuation_rate: Optional[float]
    valuation_rate: Optional[float]
    batch_no: Optional[str]
    serial_nos: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockReconciliationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    reconciliation_no: str
    purpose: str
    posting_date: datetime
    posting_time: Optional[str]
    status: StockEntryStatus
    expense_account_id: Optional[UUID]
    difference_account_id: Optional[UUID]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StockReconciliationDetailResponse(StockReconciliationResponse):
    items: List[StockReconciliationItemResponse]


# ==================== Stock Entry Endpoints ====================
@router.get("/stock-entries", response_model=PaginatedResponse[StockEntryResponse])
async def list_stock_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stock_entry_type: Optional[StockEntryType] = None,
    status: Optional[StockEntryStatus] = None,
    from_warehouse_id: Optional[UUID] = None,
    to_warehouse_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:stock_entry:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all stock entries with pagination and filters."""
    query = select(StockEntry).where(
        StockEntry.organization_id == tenant_id
    )
    
    if stock_entry_type:
        query = query.where(StockEntry.stock_entry_type == stock_entry_type)
    
    if status:
        query = query.where(StockEntry.status == status)
    
    if from_warehouse_id:
        query = query.where(StockEntry.from_warehouse_id == from_warehouse_id)
    
    if to_warehouse_id:
        query = query.where(StockEntry.to_warehouse_id == to_warehouse_id)
    
    if from_date:
        query = query.where(StockEntry.posting_date >= from_date)
    
    if to_date:
        query = query.where(StockEntry.posting_date <= to_date)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    entries = (await db.execute(
        query.order_by(StockEntry.posting_date.desc(), StockEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [StockEntryResponse.model_validate(e) for e in entries],
        total, page, page_size
    )


@router.post("/stock-entries", response_model=StockEntryDetailResponse)
async def create_stock_entry(
    data: StockEntryCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:stock_entry:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new stock entry."""
    # Validate warehouses based on entry type
    if data.stock_entry_type == StockEntryType.MATERIAL_RECEIPT:
        if not data.to_warehouse_id:
            raise HTTPException(status_code=400, detail="Target warehouse required for material receipt")
    elif data.stock_entry_type == StockEntryType.MATERIAL_ISSUE:
        if not data.from_warehouse_id:
            raise HTTPException(status_code=400, detail="Source warehouse required for material issue")
    elif data.stock_entry_type == StockEntryType.MATERIAL_TRANSFER:
        if not data.from_warehouse_id or not data.to_warehouse_id:
            raise HTTPException(status_code=400, detail="Both source and target warehouses required for transfer")
    
    # Generate stock entry number
    count = (await db.execute(
        select(func.count()).select_from(StockEntry).where(
            StockEntry.organization_id == tenant_id
        )
    )).scalar() or 0
    stock_entry_no = f"STE-{count + 1:06d}"
    
    # Calculate total value
    total_value = sum(
        (item.qty * (item.valuation_rate or item.basic_rate or 0))
        for item in data.items
    )
    
    # Create stock entry
    entry = StockEntry(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        stock_entry_no=stock_entry_no,
        total_value=total_value,
        posting_date=data.posting_date or datetime.utcnow(),
        **data.model_dump(exclude={"items"}, exclude_unset=True)
    )
    
    db.add(entry)
    await db.flush()
    
    # Create stock entry items
    items = []
    for item_data in data.items:
        # Calculate amounts
        basic_amount = None
        if item_data.basic_rate:
            basic_amount = item_data.qty * item_data.basic_rate
        
        item = StockEntryItem(
            organization_id=tenant_id,
            stock_entry_id=entry.id,
            basic_amount=basic_amount,
            **item_data.model_dump(exclude_unset=True)
        )
        db.add(item)
        items.append(item)
    
    await db.commit()
    await db.refresh(entry)
    
    # Fetch items for response
    entry_items = (await db.execute(
        select(StockEntryItem).where(StockEntryItem.stock_entry_id == entry.id)
    )).scalars().all()
    
    response = StockEntryDetailResponse.model_validate(entry)
    response.items = [StockEntryItemResponse.model_validate(i) for i in entry_items]
    
    return response


@router.get("/stock-entries/{entry_id}", response_model=StockEntryDetailResponse)
async def get_stock_entry(
    entry_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:stock_entry:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get stock entry by ID with items."""
    entry = (await db.execute(
        select(StockEntry).where(
            StockEntry.id == entry_id,
            StockEntry.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    
    # Fetch items
    items = (await db.execute(
        select(StockEntryItem).where(StockEntryItem.stock_entry_id == entry_id)
    )).scalars().all()
    
    response = StockEntryDetailResponse.model_validate(entry)
    response.items = [StockEntryItemResponse.model_validate(i) for i in items]
    
    return response


@router.patch("/stock-entries/{entry_id}", response_model=StockEntryResponse)
async def update_stock_entry(
    entry_id: UUID,
    data: StockEntryUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:stock_entry:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update stock entry (mainly for status changes)."""
    entry = (await db.execute(
        select(StockEntry).where(
            StockEntry.id == entry_id,
            StockEntry.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    
    # Prevent updates to submitted entries except for cancellation
    if entry.status == StockEntryStatus.SUBMITTED and data.status != StockEntryStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot modify submitted stock entry")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    
    # Set timestamps based on status
    if data.status == StockEntryStatus.SUBMITTED:
        entry.submitted_at = datetime.utcnow()
    elif data.status == StockEntryStatus.CANCELLED:
        entry.cancelled_at = datetime.utcnow()
    
    entry.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(entry)
    
    return StockEntryResponse.model_validate(entry)


# ==================== Stock Reconciliation Endpoints ====================
@router.get("/stock-reconciliations", response_model=PaginatedResponse[StockReconciliationResponse])
async def list_stock_reconciliations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    purpose: Optional[str] = None,
    status: Optional[StockEntryStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:reconciliation:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all stock reconciliations with pagination and filters."""
    query = select(StockReconciliation).where(
        StockReconciliation.organization_id == tenant_id
    )
    
    if purpose:
        query = query.where(StockReconciliation.purpose == purpose)
    
    if status:
        query = query.where(StockReconciliation.status == status)
    
    if from_date:
        query = query.where(StockReconciliation.posting_date >= from_date)
    
    if to_date:
        query = query.where(StockReconciliation.posting_date <= to_date)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    reconciliations = (await db.execute(
        query.order_by(StockReconciliation.posting_date.desc(), StockReconciliation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [StockReconciliationResponse.model_validate(r) for r in reconciliations],
        total, page, page_size
    )


@router.post("/stock-reconciliations", response_model=StockReconciliationDetailResponse)
async def create_stock_reconciliation(
    data: StockReconciliationCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:reconciliation:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new stock reconciliation."""
    # Generate reconciliation number
    count = (await db.execute(
        select(func.count()).select_from(StockReconciliation).where(
            StockReconciliation.organization_id == tenant_id
        )
    )).scalar() or 0
    reconciliation_no = f"RECON-{count + 1:06d}"
    
    # Create reconciliation
    reconciliation = StockReconciliation(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        reconciliation_no=reconciliation_no,
        posting_date=data.posting_date or datetime.utcnow(),
        **data.model_dump(exclude={"items"}, exclude_unset=True)
    )
    
    db.add(reconciliation)
    await db.flush()
    
    # Create reconciliation items
    # TODO: Fetch current quantities from stock ledger
    items = []
    for item_data in data.items:
        # In production, you would fetch current_qty and current_valuation_rate from stock ledger
        current_qty = 0  # Placeholder
        current_valuation_rate = None  # Placeholder
        
        qty_difference = item_data.qty - current_qty
        
        item = StockReconciliationItem(
            organization_id=tenant_id,
            reconciliation_id=reconciliation.id,
            current_qty=current_qty,
            current_valuation_rate=current_valuation_rate,
            qty_difference=qty_difference,
            **item_data.model_dump(exclude_unset=True)
        )
        db.add(item)
        items.append(item)
    
    await db.commit()
    await db.refresh(reconciliation)
    
    # Fetch items for response
    recon_items = (await db.execute(
        select(StockReconciliationItem).where(
            StockReconciliationItem.reconciliation_id == reconciliation.id
        )
    )).scalars().all()
    
    response = StockReconciliationDetailResponse.model_validate(reconciliation)
    response.items = [StockReconciliationItemResponse.model_validate(i) for i in recon_items]
    
    return response


@router.get("/stock-reconciliations/{reconciliation_id}", response_model=StockReconciliationDetailResponse)
async def get_stock_reconciliation(
    reconciliation_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:reconciliation:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get stock reconciliation by ID with items."""
    reconciliation = (await db.execute(
        select(StockReconciliation).where(
            StockReconciliation.id == reconciliation_id,
            StockReconciliation.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Stock reconciliation not found")
    
    # Fetch items
    items = (await db.execute(
        select(StockReconciliationItem).where(
            StockReconciliationItem.reconciliation_id == reconciliation_id
        )
    )).scalars().all()
    
    response = StockReconciliationDetailResponse.model_validate(reconciliation)
    response.items = [StockReconciliationItemResponse.model_validate(i) for i in items]
    
    return response


@router.patch("/stock-reconciliations/{reconciliation_id}", response_model=StockReconciliationResponse)
async def update_stock_reconciliation(
    reconciliation_id: UUID,
    data: StockReconciliationUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:reconciliation:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update stock reconciliation (mainly for status changes)."""
    reconciliation = (await db.execute(
        select(StockReconciliation).where(
            StockReconciliation.id == reconciliation_id,
            StockReconciliation.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Stock reconciliation not found")
    
    # Prevent updates to submitted reconciliations
    if reconciliation.status == StockEntryStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Cannot modify submitted reconciliation")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(reconciliation, key, value)
    
    # Set submitted timestamp
    if data.status == StockEntryStatus.SUBMITTED:
        reconciliation.submitted_at = datetime.utcnow()
    
    reconciliation.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(reconciliation)
    
    return StockReconciliationResponse.model_validate(reconciliation)
