"""Warehouse management endpoints."""
from datetime import datetime
from typing import Optional
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
from services.inventory.models.warehouse import Warehouse

router = APIRouter()

class WarehouseCreate(BaseModel):
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    is_default: bool = False

class WarehouseResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: Optional[str]
    description: Optional[str]
    city: Optional[str]
    country: Optional[str]
    is_active: bool
    is_default: bool
    created_at: datetime
    class Config:
        from_attributes = True

@router.get("", response_model=list[WarehouseResponse])
async def list_warehouses(current_user: TokenPayload = Depends(require_permissions("warehouse:list")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    warehouses = (await db.execute(select(Warehouse).where(Warehouse.organization_id == tenant_id, Warehouse.deleted_at.is_(None)).order_by(Warehouse.name))).scalars().all()
    return [WarehouseResponse.model_validate(w) for w in warehouses]

@router.post("", response_model=WarehouseResponse)
async def create_warehouse(data: WarehouseCreate, current_user: TokenPayload = Depends(require_permissions("warehouse:create")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    warehouse = Warehouse(organization_id=tenant_id, **data.model_dump(exclude_unset=True))
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    return WarehouseResponse.model_validate(warehouse)

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(warehouse_id: UUID, current_user: TokenPayload = Depends(require_permissions("warehouse:read")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    warehouse = (await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.organization_id == tenant_id))).scalar_one_or_none()
    if not warehouse: raise HTTPException(status_code=404, detail="Warehouse not found")
    return WarehouseResponse.model_validate(warehouse)

@router.delete("/{warehouse_id}", response_model=SuccessResponse)
async def delete_warehouse(warehouse_id: UUID, current_user: TokenPayload = Depends(require_permissions("warehouse:delete")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    warehouse = (await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.organization_id == tenant_id))).scalar_one_or_none()
    if not warehouse: raise HTTPException(status_code=404, detail="Warehouse not found")
    warehouse.deleted_at = datetime.utcnow()
    await db.commit()
    return SuccessResponse(message="Warehouse deleted")
