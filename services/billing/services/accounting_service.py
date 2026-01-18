from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.models.billing_accounting import (
    Invoice, Payment, ChartOfAccounts, JournalEntry, JournalEntryLine,
    JournalEntryStatus, AccountType, InvoiceType, PaymentType
)

class AccountingService:
    @staticmethod
    async def get_account_by_code(db: AsyncSession, org_id: UUID, code: str) -> Optional[ChartOfAccounts]:
        """Finds an account by organization and code."""
        result = await db.execute(
            select(ChartOfAccounts).where(
                ChartOfAccounts.organization_id == org_id,
                ChartOfAccounts.account_code == code
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def create_invoice_journal_entry(cls, db: AsyncSession, invoice: Invoice, user_id: UUID):
        """
        Creates a journal entry for a sales invoice:
        Dr. Accounts Receivable (1130)
        Cr. Sales Revenue (4100)
        Cr. Sales Tax (2130)
        """
        if invoice.invoice_type != InvoiceType.SALES:
            return  # Handle purchase or others if needed

        ar_acc = await cls.get_account_by_code(db, invoice.organization_id, "1130")
        sales_acc = await cls.get_account_by_code(db, invoice.organization_id, "4100")
        tax_acc = await cls.get_account_by_code(db, invoice.organization_id, "2130")

        if not ar_acc or not sales_acc:
            print(f"⚠️ Missing accounts (1130/4100) for org {invoice.organization_id}")
            return

        entry = JournalEntry(
            organization_id=invoice.organization_id,
            entry_no=f"JV-INV-{invoice.invoice_no}",
            entry_date=invoice.invoice_date,
            posting_date=datetime.utcnow(),
            reference_type="INVOICE",
            reference_id=invoice.id,
            reference_no=invoice.invoice_no,
            description=f"Sales record for {invoice.invoice_no}",
            total_debit=invoice.total_amount,
            total_credit=invoice.total_amount,
            status=JournalEntryStatus.POSTED,
            posted_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        db.add(entry)
        await db.flush()

        # AR Debit
        db.add(JournalEntryLine(
            organization_id=invoice.organization_id,
            journal_entry_id=entry.id,
            account_id=ar_acc.id,
            debit_amount=invoice.total_amount,
            credit_amount=0,
            description=f"AR for {invoice.invoice_no}",
            line_number=1
        ))
        ar_acc.current_balance += invoice.total_amount

        # Sales Credit (Net)
        net_sales = invoice.total_amount - (invoice.tax_amount or 0)
        db.add(JournalEntryLine(
            organization_id=invoice.organization_id,
            journal_entry_id=entry.id,
            account_id=sales_acc.id,
            debit_amount=0,
            credit_amount=net_sales,
            description=f"Sales for {invoice.invoice_no}",
            line_number=2
        ))
        sales_acc.current_balance += net_sales

        # Tax Credit
        if invoice.tax_amount and tax_acc:
            db.add(JournalEntryLine(
                organization_id=invoice.organization_id,
                journal_entry_id=entry.id,
                account_id=tax_acc.id,
                debit_amount=0,
                credit_amount=invoice.tax_amount,
                description=f"Tax for {invoice.invoice_no}",
                line_number=3
            ))
            tax_acc.current_balance += invoice.tax_amount

    @classmethod
    async def create_payment_journal_entry(cls, db: AsyncSession, payment: Payment, user_id: UUID):
        """
        Creates a journal entry for a payment received:
        Dr. Bank (1120)
        Cr. Accounts Receivable (1130)
        """
        if payment.payment_type != PaymentType.RECEIVED:
            return

        bank_acc = await cls.get_account_by_code(db, payment.organization_id, "1120")
        ar_acc = await cls.get_account_by_code(db, payment.organization_id, "1130")

        if not bank_acc or not ar_acc:
            return

        entry = JournalEntry(
            organization_id=payment.organization_id,
            entry_no=f"JV-PAY-{payment.payment_no}",
            entry_date=payment.payment_date,
            posting_date=datetime.utcnow(),
            reference_type="PAYMENT",
            reference_id=payment.id,
            reference_no=payment.payment_no,
            description=f"Payment record for {payment.payment_no}",
            total_debit=payment.amount,
            total_credit=payment.amount,
            status=JournalEntryStatus.POSTED,
            posted_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        db.add(entry)
        await db.flush()

        # Bank Debit
        db.add(JournalEntryLine(
            organization_id=payment.organization_id,
            journal_entry_id=entry.id,
            account_id=bank_acc.id,
            debit_amount=payment.amount,
            credit_amount=0,
            description=f"Cash receipt {payment.payment_no}",
            line_number=1
        ))
        bank_acc.current_balance += payment.amount

        # AR Credit
        db.add(JournalEntryLine(
            organization_id=payment.organization_id,
            journal_entry_id=entry.id,
            account_id=ar_acc.id,
            debit_amount=0,
            credit_amount=payment.amount,
            description=f"Clearing AR via {payment.payment_no}",
            line_number=2
        ))
        ar_acc.current_balance -= payment.amount
