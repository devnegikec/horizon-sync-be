from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# Customer Schemas
class CustomerBase(BaseModel):
    customer_name: str
    customer_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None

class CustomerResponse(CustomerBase):
    id: UUID
    organization_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Supplier Schemas
class SupplierBase(BaseModel):
    supplier_name: str
    supplier_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None

class SupplierResponse(SupplierBase):
    id: UUID
    organization_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Invoice Schemas
class InvoiceItemBase(BaseModel):
    item_id: Optional[UUID] = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0")

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: UUID
    invoice_id: UUID
    tax_amount: Decimal
    total_amount: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class InvoiceBase(BaseModel):
    invoice_no: str
    invoice_date: datetime = datetime.utcnow()
    due_date: Optional[datetime] = None
    invoice_type: str = "sales"
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    currency: str = "USD"
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

class InvoiceResponse(InvoiceBase):
    id: UUID
    organization_id: UUID
    status: str
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_paid: Decimal
    balance_due: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse]
    
    model_config = ConfigDict(from_attributes=True)

# Payment Schemas
class PaymentBase(BaseModel):
    payment_no: str
    payment_date: datetime = datetime.utcnow()
    payment_type: str
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    amount: Decimal
    payment_method: Optional[str] = None
    bank_account_id: Optional[UUID] = None
    reference_no: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: UUID
    organization_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Accounting Schemas
class ChartOfAccountsBase(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[UUID] = None
    is_group: bool = False
    opening_balance: Decimal = Decimal("0")
    tags: Optional[Dict[str, Any]] = None

class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass

class ChartOfAccountsResponse(ChartOfAccountsBase):
    id: UUID
    organization_id: UUID
    level: int
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class JournalEntryLineBase(BaseModel):
    account_id: UUID
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    description: Optional[str] = None

class JournalEntryLineCreate(JournalEntryLineBase):
    pass

class JournalEntryLineResponse(JournalEntryLineBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class JournalEntryBase(BaseModel):
    entry_no: str
    entry_date: datetime = datetime.utcnow()
    posting_date: Optional[datetime] = None
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    reference_no: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalEntryLineCreate]

class JournalEntryResponse(JournalEntryBase):
    id: UUID
    organization_id: UUID
    total_debit: Decimal
    total_credit: Decimal
    status: str
    posted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    lines: List[JournalEntryLineResponse]
    
    model_config = ConfigDict(from_attributes=True)
