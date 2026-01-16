"""Product management endpoints."""
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
from services.inventory.models.product import Product, ProductStatus

router = APIRouter()

class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    sku: str = Field(..., max_length=100)
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    unit_price: float = Field(default=0, ge=0)
    cost_price: Optional[float] = Field(default=None, ge=0)
    tax_rate: float = Field(default=0, ge=0, le=100)
    track_inventory: bool = True
    min_stock_level: int = Field(default=0, ge=0)
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    unit_price: Optional[float] = Field(default=None, ge=0)
    cost_price: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=100)
    status: Optional[ProductStatus] = None
    min_stock_level: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    sku: str
    barcode: Optional[str]
    description: Optional[str]
    category_id: Optional[UUID]
    unit_price: float
    cost_price: Optional[float]
    currency: str
    tax_rate: float
    track_inventory: bool
    min_stock_level: int
    status: ProductStatus
    image_url: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

@router.get("", response_model=PaginatedResponse[ProductResponse])
async def list_products(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[ProductStatus] = None, category_id: Optional[UUID] = None,
    current_user: TokenPayload = Depends(require_permissions("product:list")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    query = select(Product).where(Product.organization_id == tenant_id, Product.deleted_at.is_(None))
    if search: query = query.where(or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%")))
    if status: query = query.where(Product.status == status)
    if category_id: query = query.where(Product.category_id == category_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    products = (await db.execute(query.order_by(Product.name).offset((page-1)*page_size).limit(page_size))).scalars().all()
    return PaginatedResponse.create([ProductResponse.model_validate(p) for p in products], total, page, page_size)

@router.post("", response_model=ProductResponse)
async def create_product(data: ProductCreate, current_user: TokenPayload = Depends(require_permissions("product:create")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    # Check SKU uniqueness
    existing = (await db.execute(select(Product).where(Product.organization_id == tenant_id, Product.sku == data.sku))).scalar_one_or_none()
    if existing: raise HTTPException(status_code=409, detail="SKU already exists")
    product = Product(organization_id=tenant_id, created_by=UUID(current_user.sub), **data.model_dump(exclude_unset=True))
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, current_user: TokenPayload = Depends(require_permissions("product:read")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    product = (await db.execute(select(Product).where(Product.id == product_id, Product.organization_id == tenant_id, Product.deleted_at.is_(None)))).scalar_one_or_none()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, data: ProductUpdate, current_user: TokenPayload = Depends(require_permissions("product:update")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    product = (await db.execute(select(Product).where(Product.id == product_id, Product.organization_id == tenant_id, Product.deleted_at.is_(None)))).scalar_one_or_none()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(product, k, v)
    product.updated_by = UUID(current_user.sub)
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)

@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(product_id: UUID, current_user: TokenPayload = Depends(require_permissions("product:delete")),
    tenant_id: UUID = Depends(require_tenant), db: AsyncSession = Depends(get_async_session)):
    product = (await db.execute(select(Product).where(Product.id == product_id, Product.organization_id == tenant_id))).scalar_one_or_none()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    product.deleted_at = datetime.utcnow()
    await db.commit()
    return SuccessResponse(message="Product deleted")
