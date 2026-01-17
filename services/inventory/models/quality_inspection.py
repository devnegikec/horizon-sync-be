"""Quality Inspection models."""
import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from shared.database.base import Base, TimestampMixin, UUIDMixin, TenantMixin, AuditMixin


class InspectionStatus(str, enum.Enum):
    """Inspection status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class InspectionType(str, enum.Enum):
    """Inspection type."""
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    IN_PROCESS = "in_process"


class ReadingType(str, enum.Enum):
    """Quality parameter reading type."""
    NUMERIC = "numeric"
    TEXT = "text"
    PASS_FAIL = "pass_fail"


class QualityInspectionTemplate(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Quality inspection template with parameters."""
    __tablename__ = "quality_inspection_templates"
    
    template_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Applicable to
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    item_group_id = Column(UUID(as_uuid=True), ForeignKey("item_groups.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSONB, default=dict)


class QualityInspectionParameter(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Quality inspection parameters in template."""
    __tablename__ = "quality_inspection_parameters"
    
    template_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspection_templates.id"), nullable=False, index=True)
    
    parameter_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Reading type and acceptance criteria
    reading_type = Column(Enum(ReadingType), default=ReadingType.NUMERIC)
    
    # For numeric readings
    min_value = Column(Numeric(15, 3), nullable=True)
    max_value = Column(Numeric(15, 3), nullable=True)
    
    # For text/pass-fail
    acceptance_criteria = Column(Text, nullable=True)
    
    # Action if criteria not met
    non_conformance_action = Column(String(50), default="warn")  # warn, stop
    
    # Order
    sequence = Column(Integer, default=0)
    
    extra_data = Column(JSONB, default=dict)


class QualityInspection(Base, UUIDMixin, TimestampMixin, TenantMixin, AuditMixin):
    """Quality inspection record."""
    __tablename__ = "quality_inspections"
    
    inspection_no = Column(String(100), nullable=False, unique=True, index=True)
    
    # Item
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    item_name = Column(String(255), nullable=True)
    
    # Template
    template_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspection_templates.id"), nullable=True)
    
    # Type
    inspection_type = Column(Enum(InspectionType), default=InspectionType.INCOMING)
    
    # Reference document
    reference_type = Column(String(50), nullable=True)  # purchase_receipt, delivery_note
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Batch/Serial
    batch_no = Column(String(100), nullable=True)
    serial_no = Column(String(100), nullable=True)
    
    # Sample
    sample_size = Column(Numeric(15, 3), nullable=True)
    inspected_by = Column(UUID(as_uuid=True), nullable=True)
    inspection_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Status
    status = Column(Enum(InspectionStatus), default=InspectionStatus.PENDING)
    
    # Results
    verified = Column(Boolean, default=False)
    remarks = Column(Text, nullable=True)
    
    extra_data = Column(JSONB, default=dict)


class QualityInspectionReading(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Quality inspection readings."""
    __tablename__ = "quality_inspection_readings"
    
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspections.id"), nullable=False, index=True)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspection_parameters.id"), nullable=True)
    
    parameter_name = Column(String(255), nullable=False)
    
    # Reading
    reading_value = Column(String(255), nullable=True)
    numeric_value = Column(Numeric(15, 3), nullable=True)
    
    # Status
    status = Column(String(50), default="accepted")  # accepted, rejected
    
    remarks = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
