from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.database.session import get_db
from shared.models.billing_accounting import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, JournalEntryStatus
)
from shared.schemas.billing_accounting import (
    ChartOfAccountsCreate, ChartOfAccountsResponse,
    JournalEntryCreate, JournalEntryResponse
)
from shared.security.auth import get_current_user_id, get_current_org_id

router = APIRouter()

@router.get("/accounts", response_model=List[ChartOfAccountsResponse])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id)
):
    """List the Chart of Accounts."""
    result = await db.execute(
        select(ChartOfAccounts).where(ChartOfAccounts.organization_id == org_id).order_by(ChartOfAccounts.account_code)
    )
    return result.scalars().all()

@router.post("/accounts", response_model=ChartOfAccountsResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: ChartOfAccountsCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new account in COA."""
    # Check if code exists
    res = await db.execute(select(ChartOfAccounts).where(ChartOfAccounts.organization_id == org_id, ChartOfAccounts.account_code == account_in.account_code))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Account code already exists")

    db_account = ChartOfAccounts(
        **account_in.dict(),
        organization_id=org_id,
        current_balance=account_in.opening_balance,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account

@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_current_org_id),
    user_id: UUID = Depends(get_current_user_id)
):
    """Creates a manual journal entry. Must be balanced (Sum Dr = Sum Cr)."""
    if entry_in.total_debit != entry_in.total_credit:
        raise HTTPException(status_code=400, detail="Journal entry must be balanced (Total Debit == Total Credit)")

    db_entry = JournalEntry(
        **entry_in.dict(exclude={"lines"}),
        organization_id=org_id,
        status=JournalEntryStatus.DRAFT,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_entry)
    await db.flush()

    for i, line in enumerate(entry_in.lines):
        db_line = JournalEntryLine(
            **line.dict(),
            organization_id=org_id,
            journal_entry_id=db_entry.id,
            line_number=i+1
        )
        db.add(db_line)

    await db.commit()
    await db.refresh(db_entry)
    
    result = await db.execute(
        select(JournalEntry).options(selectinload(JournalEntry.lines)).where(JournalEntry.id == db_entry.id)
    )
    return result.scalar_one()
