from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.database.session import get_db
from shared.models.billing_accounting import Invoice, InvoiceItem, InvoiceStatus
from shared.schemas.billing_accounting import InvoiceCreate, InvoiceResponse
from shared.security.auth import get_current_user_id, get_current_org_id
from services.billing.services.accounting_service import AccountingService

router = APIRouter()

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a draft invoice."""
    # Check if number exists
    res = await db.execute(select(Invoice).where(Invoice.organization_id == org_id, Invoice.invoice_no == invoice_in.invoice_no))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Invoice number already exists")

    total_amount = sum(item.total_amount for item in invoice_in.items)
    
    db_invoice = Invoice(
        **invoice_in.dict(exclude={"items", "extra_data"}),
        organization_id=org_id,
        total_amount=total_amount,
        balance_due=total_amount,
        status=InvoiceStatus.DRAFT,
        created_by=user_id,
        updated_by=user_id,
        extra_data=invoice_in.extra_data
    )
    db.add(db_invoice)
    await db.flush()

    for item in invoice_in.items:
        db_item = InvoiceItem(
            **item.dict(),
            organization_id=org_id,
            invoice_id=db_invoice.id
        )
        db.add(db_item)

    await db.commit()
    await db.refresh(db_invoice)
    
    # Reload with items
    result = await db.execute(
        select(Invoice).options(selectinload(Invoice.items)).where(Invoice.id == db_invoice.id)
    )
    return result.scalar_one()

@router.post("/{invoice_id}/submit", response_model=InvoiceResponse)
async def submit_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Submits a draft invoice, making it SENT and creating accounting entries."""
    result = await db.execute(
        select(Invoice).options(selectinload(Invoice.items)).where(
            Invoice.id == invoice_id,
            Invoice.organization_id == org_id
        )
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only DRAFT invoices can be submitted")

    invoice.status = InvoiceStatus.SENT
    
    # Automate accounting
    await AccountingService.create_invoice_journal_entry(db, invoice, user_id)
    
    await db.commit()
    await db.refresh(invoice)
    return invoice
