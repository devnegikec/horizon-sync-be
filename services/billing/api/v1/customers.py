from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.session import get_db
from shared.models.billing_accounting import Customer
from shared.schemas.billing_accounting import CustomerCreate, CustomerUpdate, CustomerResponse
from shared.security.auth import get_current_user_id, get_current_org_id

router = APIRouter()

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new customer."""
    # Check if code already exists in org
    result = await db.execute(
        select(Customer).where(
            Customer.organization_id == org_id,
            Customer.customer_code == customer_in.customer_code
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with code {customer_in.customer_code} already exists."
        )
    
    db_customer = Customer(
        **customer_in.dict(exclude={"tags", "custom_fields", "extra_data"}),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        tags=customer_in.tags,
        custom_fields=customer_in.custom_fields,
        extra_data=customer_in.extra_data
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id)
):
    """List all customers for the organization."""
    query = select(Customer).where(
        Customer.organization_id == org_id,
        Customer.deleted_at.is_(None)
    )
    
    if q:
        query = query.where(Customer.customer_name.ilike(f"%{q}%") | Customer.customer_code.ilike(f"%{q}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id)
):
    """Get a specific customer by ID."""
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.organization_id == org_id,
            Customer.deleted_at.is_(None)
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
