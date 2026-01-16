"""Stock management endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import SuccessResponse
from shared.security.jwt import TokenPayload
from services.inventory.models.stock import StockLevel, StockMovement, MovementType

router = APIRouter()

class StockAdjustment(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: int
    movement_type: MovementType
    notes: Optional[str] = None

class StockLevelResponse(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    last_counted_at: Optional[datetime]
    class Config:
        from_attributes = True

@router.get("/levels/{product_id}", response_model=list[StockLevelResponse])
async def get_stock_levels(product_id: UUID, current_user: TokenPayload = Depends(require_permissions("inventory:read")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    levels = (await db.execute(select(StockLevel).where(StockLevel.organization_id == tenant_id, StockLevel.product_id == product_id))).scalars().all()
    return [StockLevelResponse.model_validate(l) for l in levels]

@router.post("/adjust", response_model=SuccessResponse)
async def adjust_stock(data: StockAdjustment, current_user: TokenPayload = Depends(require_permissions("inventory:update")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    # Get or create stock level
    level = (await db.execute(select(StockLevel).where(StockLevel.organization_id == tenant_id, 
        StockLevel.product_id == data.product_id, StockLevel.warehouse_id == data.warehouse_id))).scalar_one_or_none()
    
    if not level:
        level = StockLevel(organization_id=tenant_id, product_id=data.product_id, warehouse_id=data.warehouse_id)
        db.add(level)
    
    # Apply adjustment
    level.quantity_on_hand += data.quantity
    level.quantity_available = level.quantity_on_hand - level.quantity_reserved
    
    # Record movement
    movement = StockMovement(organization_id=tenant_id, product_id=data.product_id, warehouse_id=data.warehouse_id,
        movement_type=data.movement_type, quantity=data.quantity, notes=data.notes, performed_by=UUID(current_user.sub))
    db.add(movement)
    
    await db.commit()
    return SuccessResponse(message="Stock adjusted successfully")

@router.get("/movements/{product_id}")
async def get_stock_movements(product_id: UUID, warehouse_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:read")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    query = select(StockMovement).where(StockMovement.organization_id == tenant_id, StockMovement.product_id == product_id)
    if warehouse_id: query = query.where(StockMovement.warehouse_id == warehouse_id)
    query = query.order_by(StockMovement.performed_at.desc()).limit(100)
    movements = (await db.execute(query)).scalars().all()
    return [{"id": str(m.id), "movement_type": m.movement_type.value, "quantity": m.quantity, "notes": m.notes, "performed_at": m.performed_at} for m in movements]
