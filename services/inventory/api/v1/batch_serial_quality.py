"""Batch, Serial Number, and Quality Inspection endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_async_session
from shared.middleware.auth import require_permissions
from shared.middleware.tenant import require_tenant
from shared.schemas.common import PaginatedResponse, SuccessResponse
from shared.security.jwt import TokenPayload
from services.inventory.models.batch_serial import Batch, BatchStatus, SerialNo, SerialNoHistory
from services.inventory.models.quality_inspection import (
    QualityInspectionTemplate, QualityInspectionParameter,
    QualityInspection, QualityInspectionReading,
    InspectionStatus, InspectionType, ReadingType
)


router = APIRouter()


# ==================== Batch Schemas ====================
class BatchCreate(BaseModel):
    batch_no: str
    item_id: UUID
    manufacturing_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    supplier_id: Optional[UUID] = None
    supplier_batch_no: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    description: Optional[str] = None


class BatchUpdate(BaseModel):
    status: Optional[BatchStatus] = None
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None


class BatchResponse(BaseModel):
    id: UUID
    organization_id: UUID
    batch_no: str
    item_id: UUID
    manufacturing_date: Optional[datetime]
    expiry_date: Optional[datetime]
    supplier_id: Optional[UUID]
    supplier_batch_no: Optional[str]
    status: BatchStatus
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Serial Number Schemas ====================
class SerialNoCreate(BaseModel):
    serial_no: str
    item_id: UUID
    warehouse_id: Optional[UUID] = None
    purchase_date: Optional[datetime] = None
    purchase_rate: Optional[float] = None
    supplier_id: Optional[UUID] = None
    warranty_period: Optional[int] = None
    batch_no: Optional[str] = None
    description: Optional[str] = None


class SerialNoUpdate(BaseModel):
    warehouse_id: Optional[UUID] = None
    status: Optional[str] = None
    delivery_date: Optional[datetime] = None
    customer_id: Optional[UUID] = None
    warranty_expiry_date: Optional[datetime] = None
    amc_expiry_date: Optional[datetime] = None
    description: Optional[str] = None


class SerialNoResponse(BaseModel):
    id: UUID
    organization_id: UUID
    serial_no: str
    item_id: UUID
    warehouse_id: Optional[UUID]
    status: str
    purchase_date: Optional[datetime]
    purchase_rate: Optional[float]
    supplier_id: Optional[UUID]
    delivery_date: Optional[datetime]
    customer_id: Optional[UUID]
    warranty_period: Optional[int]
    warranty_expiry_date: Optional[datetime]
    amc_expiry_date: Optional[datetime]
    batch_no: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Quality Inspection Template Schemas ====================
class QualityInspectionParameterCreate(BaseModel):
    parameter_name: str
    description: Optional[str] = None
    reading_type: ReadingType = ReadingType.NUMERIC
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    acceptance_criteria: Optional[str] = None
    non_conformance_action: str = Field(default="warn")
    sequence: int = Field(default=0, ge=0)


class QualityInspectionTemplateCreate(BaseModel):
    template_name: str
    description: Optional[str] = None
    item_id: Optional[UUID] = None
    item_group_id: Optional[UUID] = None
    parameters: List[QualityInspectionParameterCreate]


class QualityInspectionTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class QualityInspectionParameterResponse(BaseModel):
    id: UUID
    template_id: UUID
    parameter_name: str
    description: Optional[str]
    reading_type: ReadingType
    min_value: Optional[float]
    max_value: Optional[float]
    acceptance_criteria: Optional[str]
    non_conformance_action: str
    sequence: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QualityInspectionTemplateResponse(BaseModel):
    id: UUID
    organization_id: UUID
    template_name: str
    description: Optional[str]
    item_id: Optional[UUID]
    item_group_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QualityInspectionTemplateDetailResponse(QualityInspectionTemplateResponse):
    parameters: List[QualityInspectionParameterResponse]


# ==================== Quality Inspection Schemas ====================
class QualityInspectionReadingCreate(BaseModel):
    parameter_id: Optional[UUID] = None
    parameter_name: str
    reading_value: Optional[str] = None
    numeric_value: Optional[float] = None
    status: str = Field(default="accepted")
    remarks: Optional[str] = None


class QualityInspectionCreate(BaseModel):
    item_id: UUID
    item_name: Optional[str] = None
    template_id: Optional[UUID] = None
    inspection_type: InspectionType = InspectionType.INCOMING
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    batch_no: Optional[str] = None
    serial_no: Optional[str] = None
    sample_size: Optional[float] = None
    inspected_by: Optional[UUID] = None
    inspection_date: Optional[datetime] = None
    remarks: Optional[str] = None
    readings: List[QualityInspectionReadingCreate]


class QualityInspectionUpdate(BaseModel):
    status: Optional[InspectionStatus] = None
    verified: Optional[bool] = None
    remarks: Optional[str] = None


class QualityInspectionReadingResponse(BaseModel):
    id: UUID
    inspection_id: UUID
    parameter_id: Optional[UUID]
    parameter_name: str
    reading_value: Optional[str]
    numeric_value: Optional[float]
    status: str
    remarks: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QualityInspectionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    inspection_no: str
    item_id: UUID
    item_name: Optional[str]
    template_id: Optional[UUID]
    inspection_type: InspectionType
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    batch_no: Optional[str]
    serial_no: Optional[str]
    sample_size: Optional[float]
    inspected_by: Optional[UUID]
    inspection_date: datetime
    status: InspectionStatus
    verified: bool
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QualityInspectionDetailResponse(QualityInspectionResponse):
    readings: List[QualityInspectionReadingResponse]


# ==================== Batch Endpoints ====================
@router.get("/batches", response_model=PaginatedResponse[BatchResponse])
async def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    item_id: Optional[UUID] = None,
    status: Optional[BatchStatus] = None,
    search: Optional[str] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:batch:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all batches with pagination and filters."""
    query = select(Batch).where(Batch.organization_id == tenant_id)
    
    if item_id:
        query = query.where(Batch.item_id == item_id)
    
    if status:
        query = query.where(Batch.status == status)
    
    if search:
        query = query.where(
            or_(
                Batch.batch_no.ilike(f"%{search}%"),
                Batch.supplier_batch_no.ilike(f"%{search}%")
            )
        )
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    batches = (await db.execute(
        query.order_by(Batch.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [BatchResponse.model_validate(b) for b in batches],
        total, page, page_size
    )


@router.post("/batches", response_model=BatchResponse)
async def create_batch(
    data: BatchCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:batch:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new batch."""
    # Check batch number uniqueness for the item
    existing = (await db.execute(
        select(Batch).where(
            Batch.organization_id == tenant_id,
            Batch.item_id == data.item_id,
            Batch.batch_no == data.batch_no
        )
    )).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=409, detail="Batch number already exists for this item")
    
    batch = Batch(
        organization_id=tenant_id,
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    
    return BatchResponse.model_validate(batch)


@router.patch("/batches/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: UUID,
    data: BatchUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:batch:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update batch."""
    batch = (await db.execute(
        select(Batch).where(
            Batch.id == batch_id,
            Batch.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(batch, key, value)
    
    await db.commit()
    await db.refresh(batch)
    
    return BatchResponse.model_validate(batch)


# ==================== Serial Number Endpoints ====================
@router.get("/serial-numbers", response_model=PaginatedResponse[SerialNoResponse])
async def list_serial_numbers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    item_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:serial:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all serial numbers with pagination and filters."""
    query = select(SerialNo).where(SerialNo.organization_id == tenant_id)
    
    if item_id:
        query = query.where(SerialNo.item_id == item_id)
    
    if warehouse_id:
        query = query.where(SerialNo.warehouse_id == warehouse_id)
    
    if status:
        query = query.where(SerialNo.status == status)
    
    if search:
        query = query.where(SerialNo.serial_no.ilike(f"%{search}%"))
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    serials = (await db.execute(
        query.order_by(SerialNo.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [SerialNoResponse.model_validate(s) for s in serials],
        total, page, page_size
    )


@router.post("/serial-numbers", response_model=SerialNoResponse)
async def create_serial_number(
    data: SerialNoCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:serial:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new serial number."""
    # Check serial number uniqueness
    existing = (await db.execute(
        select(SerialNo).where(
            SerialNo.organization_id == tenant_id,
            SerialNo.serial_no == data.serial_no
        )
    )).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=409, detail="Serial number already exists")
    
    # Calculate warranty expiry if warranty period provided
    warranty_expiry_date = None
    if data.warranty_period and data.purchase_date:
        from datetime import timedelta
        warranty_expiry_date = data.purchase_date + timedelta(days=data.warranty_period)
    
    serial = SerialNo(
        organization_id=tenant_id,
        warranty_expiry_date=warranty_expiry_date,
        **data.model_dump(exclude_unset=True)
    )
    
    db.add(serial)
    await db.commit()
    await db.refresh(serial)
    
    return SerialNoResponse.model_validate(serial)


@router.patch("/serial-numbers/{serial_id}", response_model=SerialNoResponse)
async def update_serial_number(
    serial_id: UUID,
    data: SerialNoUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:serial:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update serial number."""
    serial = (await db.execute(
        select(SerialNo).where(
            SerialNo.id == serial_id,
            SerialNo.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not serial:
        raise HTTPException(status_code=404, detail="Serial number not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(serial, key, value)
    
    await db.commit()
    await db.refresh(serial)
    
    return SerialNoResponse.model_validate(serial)


# ==================== Quality Inspection Template Endpoints ====================
@router.get("/quality-inspection-templates", response_model=PaginatedResponse[QualityInspectionTemplateResponse])
async def list_quality_inspection_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:quality_template:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all quality inspection templates."""
    query = select(QualityInspectionTemplate).where(
        QualityInspectionTemplate.organization_id == tenant_id
    )
    
    if is_active is not None:
        query = query.where(QualityInspectionTemplate.is_active == is_active)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    templates = (await db.execute(
        query.order_by(QualityInspectionTemplate.template_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [QualityInspectionTemplateResponse.model_validate(t) for t in templates],
        total, page, page_size
    )


@router.post("/quality-inspection-templates", response_model=QualityInspectionTemplateDetailResponse)
async def create_quality_inspection_template(
    data: QualityInspectionTemplateCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:quality_template:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new quality inspection template."""
    template = QualityInspectionTemplate(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        **data.model_dump(exclude={"parameters"}, exclude_unset=True)
    )
    
    db.add(template)
    await db.flush()
    
    # Create parameters
    for param_data in data.parameters:
        param = QualityInspectionParameter(
            organization_id=tenant_id,
            template_id=template.id,
            **param_data.model_dump(exclude_unset=True)
        )
        db.add(param)
    
    await db.commit()
    await db.refresh(template)
    
    # Fetch parameters for response
    parameters = (await db.execute(
        select(QualityInspectionParameter).where(
            QualityInspectionParameter.template_id == template.id
        ).order_by(QualityInspectionParameter.sequence)
    )).scalars().all()
    
    response = QualityInspectionTemplateDetailResponse.model_validate(template)
    response.parameters = [QualityInspectionParameterResponse.model_validate(p) for p in parameters]
    
    return response


# ==================== Quality Inspection Endpoints ====================
@router.get("/quality-inspections", response_model=PaginatedResponse[QualityInspectionResponse])
async def list_quality_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    item_id: Optional[UUID] = None,
    status: Optional[InspectionStatus] = None,
    inspection_type: Optional[InspectionType] = None,
    current_user: TokenPayload = Depends(require_permissions("inventory:quality_inspection:list")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """List all quality inspections."""
    query = select(QualityInspection).where(
        QualityInspection.organization_id == tenant_id
    )
    
    if item_id:
        query = query.where(QualityInspection.item_id == item_id)
    
    if status:
        query = query.where(QualityInspection.status == status)
    
    if inspection_type:
        query = query.where(QualityInspection.inspection_type == inspection_type)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    
    inspections = (await db.execute(
        query.order_by(QualityInspection.inspection_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).scalars().all()
    
    return PaginatedResponse.create(
        [QualityInspectionResponse.model_validate(i) for i in inspections],
        total, page, page_size
    )


@router.post("/quality-inspections", response_model=QualityInspectionDetailResponse)
async def create_quality_inspection(
    data: QualityInspectionCreate,
    current_user: TokenPayload = Depends(require_permissions("inventory:quality_inspection:create")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new quality inspection."""
    # Generate inspection number
    count = (await db.execute(
        select(func.count()).select_from(QualityInspection).where(
            QualityInspection.organization_id == tenant_id
        )
    )).scalar() or 0
    inspection_no = f"QI-{count + 1:06d}"
    
    inspection = QualityInspection(
        organization_id=tenant_id,
        created_by=UUID(current_user.sub),
        inspection_no=inspection_no,
        inspection_date=data.inspection_date or datetime.utcnow(),
        **data.model_dump(exclude={"readings"}, exclude_unset=True)
    )
    
    db.add(inspection)
    await db.flush()
    
    # Create readings
    for reading_data in data.readings:
        reading = QualityInspectionReading(
            organization_id=tenant_id,
            inspection_id=inspection.id,
            **reading_data.model_dump(exclude_unset=True)
        )
        db.add(reading)
    
    await db.commit()
    await db.refresh(inspection)
    
    # Fetch readings for response
    readings = (await db.execute(
        select(QualityInspectionReading).where(
            QualityInspectionReading.inspection_id == inspection.id
        )
    )).scalars().all()
    
    response = QualityInspectionDetailResponse.model_validate(inspection)
    response.readings = [QualityInspectionReadingResponse.model_validate(r) for r in readings]
    
    return response


@router.patch("/quality-inspections/{inspection_id}", response_model=QualityInspectionResponse)
async def update_quality_inspection(
    inspection_id: UUID,
    data: QualityInspectionUpdate,
    current_user: TokenPayload = Depends(require_permissions("inventory:quality_inspection:update")),
    tenant_id: UUID = Depends(require_tenant),
    db: AsyncSession = Depends(get_async_session)
):
    """Update quality inspection."""
    inspection = (await db.execute(
        select(QualityInspection).where(
            QualityInspection.id == inspection_id,
            QualityInspection.organization_id == tenant_id
        )
    )).scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Quality inspection not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inspection, key, value)
    
    inspection.updated_by = UUID(current_user.sub)
    
    await db.commit()
    await db.refresh(inspection)
    
    return QualityInspectionResponse.model_validate(inspection)
