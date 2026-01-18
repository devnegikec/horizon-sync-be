from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from shared.database.base import Base, UUIDMixin, TimestampMixin, TenantMixin

class ChartOfAccount(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "chart_of_accounts"
    
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(100), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True)

class JournalEntry(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "journal_entries"
    
    entry_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    reference = Column(String(255), nullable=True)

class JournalEntryLine(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "journal_entry_lines"
    
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id", ondelete="CASCADE"), nullable=False)
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)
