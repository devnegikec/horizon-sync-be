"""Item and Item Group management endpoints."""
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
from services.inventory.models.item import (
    Item, ItemGroup, ItemStatus, ItemType, ValuationMethod
)


router = APIRouter()


# ==================== Item Group Schemas ====================
class ItemGroupCreate(BaseModel):
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    default_valuation_method: ValuationMethod = ValuationMethod.FIFO
    default_uom: Optional[str] = None


class ItemGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    default_valuation_method: Optional[ValuationMethod] = None
    default_uom: Optional[str] = None
    is_active: Optional[bool] = None


class ItemGroupResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: Optional[str]
    description: Optional[str]
    parent_id: Optional[UUID]
    default_valuation_method: ValuationMethod
    default_uom: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Item Schemas ====================
class ItemCreate(BaseModel):
    item_code: str = Field(..., max_length=100)
    item_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    item_group_id: Optional[UUID] = None
    item_type: ItemType = ItemType.STOCK
    uom: str = Field(..., max_length=50)
    maintain_stock: bool = True
    valuation_method: ValuationMethod = ValuationMethod.FIFO
    allow_negative_stock: bool = False
    has_variants: bool = False
    variant_of: Optional[UUID] = None
    variant_attributes: Optional[dict] = None
    has_batch_no: bool = False
    has_serial_no: bool = False
    batch_number_series: Optional[str] = None
    serial_number_series: Optional[str] = None
    standard_rate: Optional[float] = None
    valuation_rate: Optional[float] = None
    enable_auto_reorder: bool = False
    reorder_level: int = Field(default=0, ge=0)
    reorder_qty: int = Field(default=0, ge=0)
    min_order_qty: int = Field(default=1, ge=1)
    max_order_qty: Optional[int] = None
    weight_per_unit: Optional[float] = None
    weight_uom: Optional[str] = None
    inspection_required_before_purchase: bool = False
    inspection_required_before_delivery: bool = False
    quality_inspection_template: Optional[UUID] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ItemUpdate(BaseModel):
    item_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    item_group_id: Optional[UUID] = None
    item_type: Optional[ItemType] = None
    uom: Optional[str] = None
    maintain_stock: Optional[bool] = None
    valuation_method: Optional[ValuationMethod] = None
    allow_negative_stock: Optional[bool] = None
    standard_rate: Optional[float] = None
    valuation_rate: Optional[float] = None
    enable_auto_reorder: Optional[bool] = None
    reorder_level: Optional[int] = Field(None, ge=0)
    reorder_qty: Optional[int] = Field(None, ge=0)
    min_order_qty: Optional[int] = Field(None, ge=1)
    max_order_qty: Optional[int] = None
    inspection_required_before_purchase: Optional[bool] = None
    inspection_required_before_delivery: Optional[bool] = None
    quality_inspection_template: Optional[UUID] = None
    barcode: Optional[str] = None
    status: Optional[ItemStatus] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ItemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    item_code: str
    item_name: str
    description: Optional[str]
    item_group_id: Optional[UUID]
    item_type: ItemType
    uom: str
    maintain_stock: bool
    valuation_method: ValuationMethod
    allow_negative_stock: bool
    has_variants: bool
    variant_of: Optional[UUID]
    variant_attributes: Optional[dict]
    has_batch_no: bool
    has_serial_no: bool
    batch_number_series: Optional[str]
    serial_number_series: Optional[str]
    standard_rate: Optional[float]
    valuation_rate: Optional[float]
    enable_auto_reorder: bool
    reorder_level: int
    reorder_qty: int
    min_order_qty: int
    max_order_qty: Optional[int]
    weight_per_unit: Optional[float]
    weight_uom: Optional[str]
    inspection_required_before_purchase: bool
    inspection_required_before_delivery: bool
    quality_inspection_template: Optional[UUID]
    barcode: Optional[str]
    status: ItemStatus
    image_url: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Item Group Endpoints ====================
@router.get("/item-groups", response_model=PaginatedResponse[ItemGroupResponse])
async def list_item_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:item_group:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all item groups with pagination and filters."""
    query = select(ItemGroup).where(
        ItemGroup.organization_id == tenant_id,
        ItemGroup.deleted_at.is_(None)
    )
    
    if search:
        query = query.where(
            or_(
                ItemGroup.name.ilike(f"%{search}%"),
                ItemGroup.code.ilike(f"%{search}%")
            )
        )
    
    if parent_id is not None:
        query = query.where(ItemGroup.parent_id == parent_id)
    
    if is_active is not None:
        query = query.where(ItemGroup.is_active == is_active)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    groups = (await db.execute(
        query.order_by(ItemGroup.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [ItemGroupResponse.model_validate(g) for g in groups],
        total, page, page_size
    )


@router.post("/item-groups", response_model=ItemGroupResponse)
async def create_item_group(
    data: ItemGroupCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:item_group:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new item group."""
    # Check if parent exists
    if data.parent_id:
        parent = (await db.execute(
            select(ItemGroup).where(
                ItemGroup.id == data.parent_id,
                ItemGroup.organization_id == tenant_id
            )
        )).scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent item group not found")
    
    # Check code uniqueness if provided
    if data.code:
        existing = (await db.execute(
            select(ItemGroup).where(
                ItemGroup.organization_id == tenant_id,
                ItemGroup.code == data.code
            )
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Item group code already exists")
    
    group = ItemGroup(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    return ItemGroupResponse.model_validate(group)


@router.get("/item-groups/{group_id}", response_model=ItemGroupResponse)
async def get_item_group(
    group_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:item_group:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get item group by ID."""
    group = (await db.execute(
        select(ItemGroup).where(
            ItemGroup.id == group_id,
            ItemGroup.organization_id == tenant_id,
            ItemGroup.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Item group not found")
    
    return ItemGroupResponse.model_validate(group)


@router.patch("/item-groups/{group_id}", response_model=ItemGroupResponse)
async def update_item_group(
    group_id: UUID,
    data: ItemGroupUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:item_group:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update item group."""
    group = (await db.execute(
        select(ItemGroup).where(
            ItemGroup.id == group_id,
            ItemGroup.organization_id == tenant_id,
            ItemGroup.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Item group not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(group, key, value)
    
    group.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(group)
    
    return ItemGroupResponse.model_validate(group)


@router.delete("/item-groups/{group_id}", response_model=SuccessResponse)
async def delete_item_group(
    group_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:item_group:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete item group."""
    group = (await db.execute(
        select(ItemGroup).where(
            ItemGroup.id == group_id,
            ItemGroup.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Item group not found")
    
    group.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Item group deleted successfully")


# ==================== Item Endpoints ====================
@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    item_group_id: Optional[UUID] = None,
    item_type: Optional[ItemType] = None,
    status: Optional[ItemStatus] = None,
    has_variants: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:item:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all items with pagination and filters."""
    query = select(Item).where(
        Item.organization_id == tenant_id,
        Item.deleted_at.is_(None)
    )
    
    if search:
        query = query.where(
            or_(
                Item.item_name.ilike(f"%{search}%"),
                Item.item_code.ilike(f"%{search}%"),
                Item.barcode.ilike(f"%{search}%")
            )
        )
    
    if item_group_id:
        query = query.where(Item.item_group_id == item_group_id)
    
    if item_type:
        query = query.where(Item.item_type == item_type)
    
    if status:
        query = query.where(Item.status == status)
    
    if has_variants is not None:
        query = query.where(Item.has_variants == has_variants)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    items = (await db.execute(
        query.order_by(Item.item_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [ItemResponse.model_validate(i) for i in items],
        total, page, page_size
    )


@router.post("/items", response_model=ItemResponse)
async def create_item(
    data: ItemCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:item:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new item."""
    # Check item code uniqueness
    existing = (await db.execute(
        select(Item).where(
            Item.organization_id == tenant_id,
            Item.item_code == data.item_code
        )
    )).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=409, detail="Item code already exists")
    
    # Check barcode uniqueness if provided
    if data.barcode:
        existing_barcode = (await db.execute(
            select(Item).where(
                Item.organization_id == tenant_id,
                Item.barcode == data.barcode
            )
        )).scalar_one_or_none()
        if existing_barcode:
            raise HTTPException(status_code=409, detail="Barcode already exists")
    
    # Validate variant_of if provided
    if data.variant_of:
        parent = (await db.execute(
            select(Item).where(
                Item.id == data.variant_of,
                Item.organization_id == tenant_id
            )
        )).scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent item not found")
        if not parent.has_variants:
            raise HTTPException(status_code=400, detail="Parent item does not support variants")
    
    item = Item(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return ItemResponse.model_validate(item)


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:item:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get item by ID."""
    item = (await db.execute(
        select(Item).where(
            Item.id == item_id,
            Item.organization_id == tenant_id,
            Item.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse.model_validate(item)


@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:item:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update item."""
    item = (await db.execute(
        select(Item).where(
            Item.id == item_id,
            Item.organization_id == tenant_id,
            Item.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check barcode uniqueness if being updated
    if data.barcode and data.barcode != item.barcode:
        existing_barcode = (await db.execute(
            select(Item).where(
                Item.organization_id == tenant_id,
                Item.barcode == data.barcode,
                Item.id != item_id
            )
        )).scalar_one_or_none()
        if existing_barcode:
            raise HTTPException(status_code=409, detail="Barcode already exists")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    
    item.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(item)
    
    return ItemResponse.model_validate(item)


@router.delete("/items/{item_id}", response_model=SuccessResponse)
async def delete_item(
    item_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:item:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete item."""
    item = (await db.execute(
        select(Item).where(
            Item.id == item_id,
            Item.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Item deleted successfully")
