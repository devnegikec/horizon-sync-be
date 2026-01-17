"""Delivery Note and Purchase Receipt models."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class DocumentStatus(str, enum.Enum):
    """Common document status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class DeliveryNote(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Delivery Note for customer deliveries."""
    __tablename__ = "delivery_notes"
    
    delivery_note_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Customer
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    customer_name = Column(String(255), nullable=True)
    
    # Reference
    sales_order_id = Column(UUID(as_uuid=True), nullable=True)
    pick_list_id = Column(UUID(as_uuid=True), ForeignKey("pick_lists.id"), nullable=True)
    
    # Dates
    posting_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    
    # Warehouse
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses_extended.id"), nullable=False)
    
    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    # Shipping
    shipping_address_line1 = Column(String(255), nullable=True)
    shipping_address_line2 = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(100), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(100), nullable=True)
    
    # Tracking
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(100), nullable=True)
    
    # Totals
    total_qty = Column(Numeric(15, 3), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Tolerances applied
    over_delivery_percentage = Column(Numeric(5, 2), default=0)
    
    # Invoice reference
    sales_invoice_id = Column(UUID(as_uuid=True), nullable=True)
    
    remarks = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)


class DeliveryNoteItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Delivery Note items."""
    __tablename__ = "delivery_note_items"
    
    delivery_note_id = Column(UUID(as_uuid=True), ForeignKey("delivery_notes.id"), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    item_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Warehouse
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses_extended.id"), nullable=False)
    
    # Quantity
    qty = Column(Numeric(15, 3), nullable=False)
    uom = Column(String(50), nullable=False)
    
    # Pricing
    rate = Column(Numeric(15, 2), nullable=True)
    amount = Column(Numeric(15, 2), nullable=True)
    
    # Reference to sales order item
    sales_order_item_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_nos = Column(JSONB, default=list)
    
    # Quality
    quality_inspection_id = Column(UUID(as_uuid=True), nullable=True)
    
    extra_data = Column(JSONB, default=dict)


class PurchaseReceipt(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Purchase Receipt for supplier deliveries."""
    __tablename__ = "purchase_receipts"
    
    purchase_receipt_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Supplier
    supplier_id = Column(UUID(as_uuid=True), nullable=False)
    supplier_name = Column(String(255), nullable=True)
    
    # Reference
    purchase_order_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Dates
    posting_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Warehouse
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses_extended.id"), nullable=False)
    
    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    # Supplier details
    supplier_delivery_note = Column(String(100), nullable=True)
    supplier_invoice_no = Column(String(100), nullable=True)
    
    # Totals
    total_qty = Column(Numeric(15, 3), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Tolerances applied
    over_receipt_percentage = Column(Numeric(5, 2), default=0)
    
    # Put-away
    apply_putaway_rule = Column(Boolean, default=False)
    
    # Invoice reference
    purchase_invoice_id = Column(UUID(as_uuid=True), nullable=True)
    
    remarks = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)


class PurchaseReceiptItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Purchase Receipt items."""
    __tablename__ = "purchase_receipt_items"
    
    purchase_receipt_id = Column(UUID(as_uuid=True), ForeignKey("purchase_receipts.id"), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    item_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Warehouse (can be overridden by put-away rule)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses_extended.id"), nullable=False)
    
    # Quantity
    qty = Column(Numeric(15, 3), nullable=False)
    received_qty = Column(Numeric(15, 3), nullable=True)  # Actual received
    uom = Column(String(50), nullable=False)
    
    # Pricing
    rate = Column(Numeric(15, 2), nullable=True)
    amount = Column(Numeric(15, 2), nullable=True)
    
    # Reference to purchase order item
    purchase_order_item_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_nos = Column(JSONB, default=list)
    
    # Quality
    quality_inspection_id = Column(UUID(as_uuid=True), nullable=True)
    
    extra_data = Column(JSONB, default=dict)


class LandedCostVoucher(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Landed Cost Voucher for additional costs on purchases."""
    __tablename__ = "landed_cost_vouchers"
    
    voucher_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Dates
    posting_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    # Distribution method
    distribute_charges_based_on = Column(String(50), default="qty")  # qty, amount
    
    # Total
    total_landed_cost = Column(Numeric(15, 2), default=0)
    
    remarks = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), nullable=True)


class LandedCostPurchaseReceipt(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Purchase receipts linked to landed cost voucher."""
    __tablename__ = "landed_cost_purchase_receipts"
    
    landed_cost_voucher_id = Column(UUID(as_uuid=True), ForeignKey("landed_cost_vouchers.id"), nullable=False, index=True)
    purchase_receipt_id = Column(UUID(as_uuid=True), ForeignKey("purchase_receipts.id"), nullable=False)
    
    grand_total = Column(Numeric(15, 2), default=0)


class LandedCostItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Items from purchase receipts in landed cost voucher."""
    __tablename__ = "landed_cost_items"
    
    landed_cost_voucher_id = Column(UUID(as_uuid=True), ForeignKey("landed_cost_vouchers.id"), nullable=False, index=True)
    purchase_receipt_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_receipt_items.id"), nullable=False)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    qty = Column(Numeric(15, 3), nullable=False)
    rate = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Allocated landed cost
    applicable_charges = Column(Numeric(15, 2), default=0)


class LandedCostTaxesAndCharges(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Additional charges/taxes for landed cost."""
    __tablename__ = "landed_cost_taxes_and_charges"
    
    landed_cost_voucher_id = Column(UUID(as_uuid=True), ForeignKey("landed_cost_vouchers.id"), nullable=False, index=True)
    
    expense_account_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
