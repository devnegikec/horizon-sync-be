from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.session import get_db
from shared.models.billing_accounting import Supplier
from shared.schemas.billing_accounting import SupplierCreate, SupplierUpdate, SupplierResponse
from shared.security.auth import get_current_user_id, get_current_org_id

router = APIRouter()

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_in: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new supplier."""
    result = await db.execute(
        select(Supplier).where(
            Supplier.organization_id == org_id,
            Supplier.supplier_code == supplier_in.supplier_code
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supplier with code {supplier_in.supplier_code} already exists."
        )
    
    db_supplier = Supplier(
        **supplier_in.dict(exclude={"tags", "custom_fields", "extra_data"}),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        tags=supplier_in.tags,
        custom_fields=supplier_in.custom_fields,
        extra_data=supplier_in.extra_data
    )
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier

@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id)
):
    """List all suppliers."""
    query = select(Supplier).where(
        Supplier.organization_id == org_id,
        Supplier.deleted_at.is_(None)
    )
    if q:
        query = query.where(Supplier.supplier_name.ilike(f"%{q}%") | Supplier.supplier_code.ilike(f"%{q}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
