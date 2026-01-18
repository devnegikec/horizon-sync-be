from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.database.session import get_db
from shared.models.billing_accounting import Payment, PaymentAllocation, PaymentStatus, Invoice
from shared.schemas.billing_accounting import PaymentCreate, PaymentResponse
from shared.security.auth import get_current_user_id, get_current_org_id
from services.billing.services.accounting_service import AccountingService

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Record a payment and optionally allocate to invoices."""
    # Check if number exists
    res = await db.execute(select(Payment).where(Payment.organization_id == org_id, Payment.payment_no == payment_in.payment_no))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Payment number already exists")

    db_payment = Payment(
        **payment_in.dict(exclude={"allocations", "extra_data"}),
        organization_id=org_id,
        status=PaymentStatus.COMPLETED,
        created_by=user_id,
        updated_by=user_id,
        extra_data=payment_in.extra_data
    )
    db.add(db_payment)
    await db.flush()

    if payment_in.allocations:
        for alloc in payment_in.allocations:
            db_alloc = PaymentAllocation(
                organization_id=org_id,
                payment_id=db_payment.id,
                invoice_id=alloc.invoice_id,
                allocated_amount=alloc.allocated_amount
            )
            db.add(db_alloc)
            
            # Update invoice paid status (logic can be in trigger but we do it simple here)
            inv_res = await db.execute(select(Invoice).where(Invoice.id == alloc.invoice_id))
            invoice = inv_res.scalar_one_or_none()
            if invoice:
                invoice.total_paid += alloc.allocated_amount
                invoice.balance_due -= alloc.allocated_amount

    # Automate accounting
    await AccountingService.create_payment_journal_entry(db, db_payment, user_id)

    await db.commit()
    
    # Reload
    result = await db.execute(
        select(Payment).options(selectinload(Payment.allocations)).where(Payment.id == db_payment.id)
    )
    return result.scalar_one()
