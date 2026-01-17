"""Warehouse, Put-away Rules, and Pick List management endpoints."""
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
from services.inventory.models.warehouse_extended import (
    WarehouseExtended, WarehouseType, PutAwayRule, PickList, PickListItem
)


router = APIRouter()


# ==================== Warehouse Schemas ====================
class WarehouseCreate(BaseModel):
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_warehouse_id: Optional[UUID] = None
    warehouse_type: WarehouseType = WarehouseType.STANDARD
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    total_capacity: Optional[int] = None
    capacity_uom: Optional[str] = None
    stock_account_id: Optional[UUID] = None
    is_default: bool = False


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_warehouse_id: Optional[UUID] = None
    warehouse_type: Optional[WarehouseType] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    total_capacity: Optional[int] = None
    capacity_uom: Optional[str] = None
    stock_account_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class WarehouseResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: Optional[str]
    description: Optional[str]
    parent_warehouse_id: Optional[UUID]
    warehouse_type: WarehouseType
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    total_capacity: Optional[int]
    capacity_uom: Optional[str]
    stock_account_id: Optional[UUID]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Put-Away Rule Schemas ====================
class PutAwayRuleCreate(BaseModel):
    name: str = Field(..., max_length=255)
    item_id: Optional[UUID] = None
    item_group_id: Optional[UUID] = None
    warehouse_id: UUID
    capacity: Optional[int] = None
    priority: int = Field(default=1, ge=1)
    min_qty: int = Field(default=0, ge=0)
    max_qty: Optional[int] = None


class PutAwayRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    item_id: Optional[UUID] = None
    item_group_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    capacity: Optional[int] = None
    priority: Optional[int] = Field(None, ge=1)
    min_qty: Optional[int] = Field(None, ge=0)
    max_qty: Optional[int] = None
    is_active: Optional[bool] = None


class PutAwayRuleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    item_id: Optional[UUID]
    item_group_id: Optional[UUID]
    warehouse_id: UUID
    capacity: Optional[int]
    priority: int
    min_qty: int
    max_qty: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Pick List Schemas ====================
class PickListItemCreate(BaseModel):
    item_id: UUID
    warehouse_id: UUID
    qty_to_pick: int = Field(..., gt=0)
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None
    bin_location: Optional[str] = None


class PickListCreate(BaseModel):
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    warehouse_id: UUID
    pick_date: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None
    items: List[PickListItemCreate]


class PickListItemUpdate(BaseModel):
    qty_picked: int = Field(..., ge=0)
    batch_no: Optional[str] = None
    serial_nos: Optional[List[str]] = None


class PickListUpdate(BaseModel):
    status: Optional[str] = None
    pick_date: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None


class PickListItemResponse(BaseModel):
    id: UUID
    pick_list_id: UUID
    item_id: UUID
    warehouse_id: UUID
    qty_to_pick: int
    qty_picked: int
    batch_no: Optional[str]
    serial_nos: List[str]
    bin_location: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PickListResponse(BaseModel):
    id: UUID
    organization_id: UUID
    pick_list_no: str
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    warehouse_id: UUID
    status: str
    pick_date: Optional[datetime]
    completed_at: Optional[datetime]
    assigned_to: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PickListDetailResponse(PickListResponse):
    items: List[PickListItemResponse]


# ==================== Warehouse Endpoints ====================
@router.get("/warehouses", response_model=PaginatedResponse[WarehouseResponse])
async def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    warehouse_type: Optional[WarehouseType] = None,
    is_active: Optional[bool] = None,
    parent_warehouse_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:warehouse:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all warehouses with pagination and filters."""
    query = select(WarehouseExtended).where(
        WarehouseExtended.organization_id == tenant_id,
        WarehouseExtended.deleted_at.is_(None)
    )
    
    if search:
        query = query.where(
            or_(
                WarehouseExtended.name.ilike(f"%{search}%"),
                WarehouseExtended.code.ilike(f"%{search}%")
            )
        )
    
    if warehouse_type:
        query = query.where(WarehouseExtended.warehouse_type == warehouse_type)
    
    if is_active is not None:
        query = query.where(WarehouseExtended.is_active == is_active)
    
    if parent_warehouse_id is not None:
        query = query.where(WarehouseExtended.parent_warehouse_id == parent_warehouse_id)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    warehouses = (await db.execute(
        query.order_by(WarehouseExtended.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [WarehouseResponse.model_validate(w) for w in warehouses],
        total, page, page_size
    )


@router.post("/warehouses", response_model=WarehouseResponse)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:warehouse:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new warehouse."""
    # Check code uniqueness if provided
    if data.code:
        existing = (await db.execute(
            select(WarehouseExtended).where(
                WarehouseExtended.organization_id == tenant_id,
                WarehouseExtended.code == data.code
            )
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Warehouse code already exists")
    
    # Check parent warehouse exists
    if data.parent_warehouse_id:
        parent = (await db.execute(
            select(WarehouseExtended).where(
                WarehouseExtended.id == data.parent_warehouse_id,
                WarehouseExtended.organization_id == tenant_id
            )
        )).scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent warehouse not found")
    
    # Generate warehouse code if not provided
    if not data.code:
        # Simple auto-generation logic
        count = (await db.execute(
            select(func.count()).select_from(WarehouseExtended).where(
                WarehouseExtended.organization_id == tenant_id
            )
        )).scalar() or 0
        data.code = f"WH-{count + 1:04d}"
    
    warehouse = WarehouseExtended(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    
    return WarehouseResponse.model_validate(warehouse)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:warehouse:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get warehouse by ID."""
    warehouse = (await db.execute(
        select(WarehouseExtended).where(
            WarehouseExtended.id == warehouse_id,
            WarehouseExtended.organization_id == tenant_id,
            WarehouseExtended.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    return WarehouseResponse.model_validate(warehouse)


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    data: WarehouseUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:warehouse:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update warehouse."""
    warehouse = (await db.execute(
        select(WarehouseExtended).where(
            WarehouseExtended.id == warehouse_id,
            WarehouseExtended.organization_id == tenant_id,
            WarehouseExtended.deleted_at.is_(None)
        )
    )).scalar_one_or_none()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)
    
    warehouse.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(warehouse)
    
    return WarehouseResponse.model_validate(warehouse)


@router.delete("/warehouses/{warehouse_id}", response_model=SuccessResponse)
async def delete_warehouse(
    warehouse_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:warehouse:delete")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Soft delete warehouse."""
    warehouse = (await db.execute(
        select(WarehouseExtended).where(
            WarehouseExtended.id == warehouse_id,
            WarehouseExtended.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    warehouse.deleted_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Warehouse deleted successfully")


# ==================== Put-Away Rule Endpoints ====================
@router.get("/put-away-rules", response_model=PaginatedResponse[PutAwayRuleResponse])
async def list_put_away_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[UUID] = None,
    item_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:putaway:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all put-away rules with pagination and filters."""
    query = select(PutAwayRule).where(
        PutAwayRule.organization_id == tenant_id
    )
    
    if warehouse_id:
        query = query.where(PutAwayRule.warehouse_id == warehouse_id)
    
    if item_id:
        query = query.where(PutAwayRule.item_id == item_id)
    
    if is_active is not None:
        query = query.where(PutAwayRule.is_active == is_active)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    rules = (await db.execute(
        query.order_by(PutAwayRule.priority, PutAwayRule.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [PutAwayRuleResponse.model_validate(r) for r in rules],
        total, page, page_size
    )


@router.post("/put-away-rules", response_model=PutAwayRuleResponse)
async def create_put_away_rule(
    data: PutAwayRuleCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:putaway:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new put-away rule."""
    rule = PutAwayRule(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return PutAwayRuleResponse.model_validate(rule)


@router.patch("/put-away-rules/{rule_id}", response_model=PutAwayRuleResponse)
async def update_put_away_rule(
    rule_id: UUID,
    data: PutAwayRuleUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:putaway:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update put-away rule."""
    rule = (await db.execute(
        select(PutAwayRule).where(
            PutAwayRule.id == rule_id,
            PutAwayRule.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Put-away rule not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    
    rule.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(rule)
    
    return PutAwayRuleResponse.model_validate(rule)


# ==================== Pick List Endpoints ====================
@router.get("/pick-lists", response_model=PaginatedResponse[PickListResponse])
async def list_pick_lists(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    warehouse_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:picklist:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all pick lists with pagination and filters."""
    query = select(PickList).where(
        PickList.organization_id == tenant_id
    )
    
    if status:
        query = query.where(PickList.status == status)
    
    if warehouse_id:
        query = query.where(PickList.warehouse_id == warehouse_id)
    
    if assigned_to:
        query = query.where(PickList.assigned_to == assigned_to)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    pick_lists = (await db.execute(
        query.order_by(PickList.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [PickListResponse.model_validate(pl) for pl in pick_lists],
        total, page, page_size
    )


@router.post("/pick-lists", response_model=PickListDetailResponse)
async def create_pick_list(
    data: PickListCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:picklist:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new pick list."""
    # Generate pick list number
    count = (await db.execute(
        select(func.count()).select_from(PickList).where(
            PickList.organization_id == tenant_id
        )
    )).scalar() or 0
    pick_list_no = f"PL-{count + 1:06d}"
    
    # Create pick list
    pick_list = PickList(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        pick_list_no=pick_list_no,
        **data.model_dump(exclude={"items"}, exclude_unset=True)
    )
    
    db.add(pick_list)
    await db.flush()
    
    # Create pick list items
    items = []
    for item_data in data.items:
        item = PickListItem(
            organization_id=tenant_id,
            pick_list_id=pick_list.id,
            **item_data.model_dump(exclude_unset=True)
        )
        db.add(item)
        items.append(item)
    
    await db.commit()
    await db.refresh(pick_list)
    
    # Fetch items for response
    pick_list_items = (await db.execute(
        select(PickListItem).where(PickListItem.pick_list_id == pick_list.id)
    )).scalars().all()
    
    response = PickListDetailResponse.model_validate(pick_list)
    response.items = [PickListItemResponse.model_validate(i) for i in pick_list_items]
    
    return response


@router.get("/pick-lists/{pick_list_id}", response_model=PickListDetailResponse)
async def get_pick_list(
    pick_list_id: UUID,
    current_user: TokenPayload = Depends(require_permissions("inventory:picklist:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get pick list by ID with items."""
    pick_list = (await db.execute(
        select(PickList).where(
            PickList.id == pick_list_id,
            PickList.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not pick_list:
        raise HTTPException(status_code=404, detail="Pick list not found")
    
    # Fetch items
    items = (await db.execute(
        select(PickListItem).where(PickListItem.pick_list_id == pick_list_id)
    )).scalars().all()
    
    response = PickListDetailResponse.model_validate(pick_list)
    response.items = [PickListItemResponse.model_validate(i) for i in items]
    
    return response


@router.patch("/pick-lists/{pick_list_id}", response_model=PickListResponse)
async def update_pick_list(
    pick_list_id: UUID,
    data: PickListUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:picklist:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update pick list status and details."""
    pick_list = (await db.execute(
        select(PickList).where(
            PickList.id == pick_list_id,
            PickList.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not pick_list:
        raise HTTPException(status_code=404, detail="Pick list not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pick_list, key, value)
    
    # Set completed_at if status is completed
    if data.status == "completed":
        pick_list.completed_at = datetime.utcnow()
    
    pick_list.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(pick_list)
    
    return PickListResponse.model_validate(pick_list)


@router.patch("/pick-lists/{pick_list_id}/items/{item_id}", response_model=PickListItemResponse)
async def update_pick_list_item(
    pick_list_id: UUID,
    item_id: UUID,
    data: PickListItemUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:picklist:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update picked quantity for a pick list item."""
    item = (await db.execute(
        select(PickListItem).where(
            PickListItem.id == item_id,
            PickListItem.pick_list_id == pick_list_id,
            PickListItem.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Pick list item not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    
    await db.commit()
    await db.refresh(item)
    
    return PickListItemResponse.model_validate(item)
