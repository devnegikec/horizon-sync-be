"""Stock Settings endpoints."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.security.jwt import TokenPayload
from services.inventory.models.settings import StockSettings


router = APIRouter()


# ==================== Stock Settings Schemas ====================
class StockSettingsCreate(BaseModel):
    item_naming_by: str = Field(default="naming_series")
    item_naming_series: Optional[str] = None
    stock_entry_naming_series: Optional[str] = None
    delivery_note_naming_series: Optional[str] = None
    purchase_receipt_naming_series: Optional[str] = None
    default_warehouse_id: Optional[UUID] = None
    allow_negative_stock: bool = False
    over_delivery_receipt_allowance: float = Field(default=0, ge=0, le=100)
    over_billing_allowance: float = Field(default=0, ge=0, le=100)
    auto_indent: bool = False
    auto_indent_notification: Optional[List[str]] = None
    default_valuation_method: str = Field(default="fifo")
    auto_create_serial_no: bool = False
    default_quality_inspection_template_id: Optional[UUID] = None
    stock_frozen_upto: Optional[str] = None
    stock_frozen_upto_days: int = Field(default=0, ge=0)
    show_barcode_field: bool = True
    convert_item_desc_to_transaction_desc: bool = False


class StockSettingsUpdate(BaseModel):
    item_naming_by: Optional[str] = None
    item_naming_series: Optional[str] = None
    stock_entry_naming_series: Optional[str] = None
    delivery_note_naming_series: Optional[str] = None
    purchase_receipt_naming_series: Optional[str] = None
    default_warehouse_id: Optional[UUID] = None
    allow_negative_stock: Optional[bool] = None
    over_delivery_receipt_allowance: Optional[float] = Field(None, ge=0, le=100)
    over_billing_allowance: Optional[float] = Field(None, ge=0, le=100)
    auto_indent: Optional[bool] = None
    auto_indent_notification: Optional[List[str]] = None
    default_valuation_method: Optional[str] = None
    auto_create_serial_no: Optional[bool] = None
    default_quality_inspection_template_id: Optional[UUID] = None
    stock_frozen_upto: Optional[str] = None
    stock_frozen_upto_days: Optional[int] = Field(None, ge=0)
    show_barcode_field: Optional[bool] = None
    convert_item_desc_to_transaction_desc: Optional[bool] = None


class StockSettingsResponse(BaseModel):
    id: UUID
    organization_id: UUID
    item_naming_by: str
    item_naming_series: Optional[str]
    stock_entry_naming_series: Optional[str]
    delivery_note_naming_series: Optional[str]
    purchase_receipt_naming_series: Optional[str]
    default_warehouse_id: Optional[UUID]
    allow_negative_stock: bool
    over_delivery_receipt_allowance: float
    over_billing_allowance: float
    auto_indent: bool
    auto_indent_notification: List[str]
    default_valuation_method: str
    auto_create_serial_no: bool
    default_quality_inspection_template_id: Optional[UUID]
    stock_frozen_upto: Optional[str]
    stock_frozen_upto_days: int
    show_barcode_field: bool
    convert_item_desc_to_transaction_desc: bool
    
    class Config:
        from_attributes = True


# ==================== Stock Settings Endpoints ====================
@router.get("/settings", response_model=StockSettingsResponse)
async def get_stock_settings(
    current_user: TokenPayload = Depends(require_permissions("inventory:settings:read")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Get stock settings for the organization."""
    settings = (await db.execute(
        select(StockSettings).where(
            StockSettings.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not settings:
        # Create default settings if not exists
        settings = StockSettings(
            organization_id=tenant_id,
            created_by=UUID(current_user.sub)
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return StockSettingsResponse.model_validate(settings)


@router.post("/settings", response_model=StockSettingsResponse)
async def create_stock_settings(
    data: StockSettingsCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:settings:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create stock settings for the organization."""
    # Check if settings already exist
    existing = (await db.execute(
        select(StockSettings).where(
            StockSettings.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=409, detail="Stock settings already exist for this organization")
    
    settings = StockSettings(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    
    return StockSettingsResponse.model_validate(settings)


@router.patch("/settings", response_model=StockSettingsResponse)
async def update_stock_settings(
    data: StockSettingsUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:settings:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update stock settings for the organization."""
    settings = (await db.execute(
        select(StockSettings).where(
            StockSettings.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Stock settings not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    
    settings.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(settings)
    
    return StockSettingsResponse.model_validate(settings)
