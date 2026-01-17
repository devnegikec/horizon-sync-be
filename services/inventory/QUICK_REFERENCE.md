# Inventory Management System - Quick Reference Guide

## Quick Start

### 1. Database Setup
```bash
# Run migrations (from project root)
alembic upgrade head
```

### 2. Start Service
```bash
# Development
uvicorn services.inventory.main:app --reload --port 8003

# Production (via Docker)
docker-compose up inventory
```

### 3. Access API Documentation
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

---

## Common API Workflows

### Initial Setup Workflow

```bash
# 1. Configure Stock Settings
POST /api/v1/stock-settings/settings
{
  "allow_negative_stock": false,
  "over_delivery_receipt_allowance": 10,
  "auto_indent": true,
  "default_valuation_method": "fifo"
}

# 2. Create Warehouses
POST /api/v1/warehouse/warehouses
{
  "name": "Main Warehouse",
  "code": "WH-MAIN",
  "warehouse_type": "standard",
  "is_default": true
}

# 3. Create Item Groups
POST /api/v1/inventory/item-groups
{
  "name": "Raw Materials",
  "code": "RM",
  "default_valuation_method": "fifo",
  "default_uom": "Kg"
}

# 4. Create Items
POST /api/v1/inventory/items
{
  "item_code": "RM-001",
  "item_name": "Steel Sheet",
  "item_group_id": "{item_group_id}",
  "uom": "Kg",
  "standard_rate": 50.00,
  "enable_auto_reorder": true,
  "reorder_level": 100,
  "reorder_qty": 500
}
```

### Purchase Flow

```bash
# 1. Create Purchase Receipt
POST /api/v1/transactions/purchase-receipts
{
  "supplier_id": "{supplier_id}",
  "warehouse_id": "{warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "warehouse_id": "{warehouse_id}",
      "qty": 1000,
      "uom": "Kg",
      "rate": 45.00
    }
  ]
}

# 2. (Optional) Add Landed Costs
POST /api/v1/transactions/landed-cost-vouchers
{
  "purchase_receipt_ids": ["{receipt_id}"],
  "taxes_and_charges": [
    {
      "expense_account_id": "{account_id}",
      "description": "Freight",
      "amount": 500.00
    }
  ]
}

# 3. Update Status to Submitted
PATCH /api/v1/transactions/purchase-receipts/{receipt_id}
{
  "status": "submitted"
}
```

### Sales Flow

```bash
# 1. Create Pick List (from Sales Order)
POST /api/v1/warehouse/pick-lists
{
  "reference_type": "sales_order",
  "reference_id": "{sales_order_id}",
  "warehouse_id": "{warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "warehouse_id": "{warehouse_id}",
      "qty_to_pick": 50
    }
  ]
}

# 2. Update Picked Quantities
PATCH /api/v1/warehouse/pick-lists/{pick_list_id}/items/{item_id}
{
  "qty_picked": 50
}

# 3. Create Delivery Note
POST /api/v1/transactions/delivery-notes
{
  "customer_id": "{customer_id}",
  "pick_list_id": "{pick_list_id}",
  "warehouse_id": "{warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "warehouse_id": "{warehouse_id}",
      "qty": 50,
      "uom": "Nos",
      "rate": 100.00
    }
  ]
}

# 4. Submit Delivery Note
PATCH /api/v1/transactions/delivery-notes/{delivery_note_id}
{
  "status": "submitted"
}
```

### Stock Transfer Flow

```bash
# Create Stock Entry (Transfer)
POST /api/v1/stock-transactions/stock-entries
{
  "stock_entry_type": "material_transfer",
  "from_warehouse_id": "{source_warehouse_id}",
  "to_warehouse_id": "{target_warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "source_warehouse_id": "{source_warehouse_id}",
      "target_warehouse_id": "{target_warehouse_id}",
      "qty": 100,
      "uom": "Nos",
      "valuation_rate": 50.00
    }
  ]
}

# Submit Entry
PATCH /api/v1/stock-transactions/stock-entries/{entry_id}
{
  "status": "submitted"
}
```

### Opening Stock Flow

```bash
# Create Stock Reconciliation
POST /api/v1/stock-transactions/stock-reconciliations
{
  "purpose": "opening_stock",
  "posting_date": "2026-01-01T00:00:00Z",
  "items": [
    {
      "item_id": "{item_id}",
      "warehouse_id": "{warehouse_id}",
      "qty": 1000,
      "valuation_rate": 45.00
    }
  ]
}

# Submit Reconciliation
PATCH /api/v1/stock-transactions/stock-reconciliations/{reconciliation_id}
{
  "status": "submitted"
}
```

### Quality Inspection Flow

```bash
# 1. Create Quality Inspection Template
POST /api/v1/tracking/quality-inspection-templates
{
  "template_name": "Raw Material QC",
  "item_group_id": "{item_group_id}",
  "parameters": [
    {
      "parameter_name": "Weight",
      "reading_type": "numeric",
      "min_value": 95.0,
      "max_value": 105.0,
      "non_conformance_action": "stop",
      "sequence": 1
    }
  ]
}

# 2. Create Quality Inspection (on Purchase Receipt)
POST /api/v1/tracking/quality-inspections
{
  "item_id": "{item_id}",
  "template_id": "{template_id}",
  "inspection_type": "incoming",
  "reference_type": "purchase_receipt",
  "reference_id": "{receipt_id}",
  "readings": [
    {
      "parameter_name": "Weight",
      "numeric_value": 98.5,
      "status": "accepted"
    }
  ]
}

# 3. Update Inspection Status
PATCH /api/v1/tracking/quality-inspections/{inspection_id}
{
  "status": "accepted",
  "verified": true
}
```

### Batch Tracking Flow

```bash
# 1. Create Batch
POST /api/v1/tracking/batches
{
  "batch_no": "BATCH-2026-001",
  "item_id": "{item_id}",
  "manufacturing_date": "2026-01-01T00:00:00Z",
  "expiry_date": "2027-01-01T00:00:00Z"
}

# 2. Use in Stock Entry
POST /api/v1/stock-transactions/stock-entries
{
  "stock_entry_type": "material_receipt",
  "to_warehouse_id": "{warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "target_warehouse_id": "{warehouse_id}",
      "qty": 100,
      "uom": "Nos",
      "batch_no": "BATCH-2026-001",
      "valuation_rate": 50.00
    }
  ]
}
```

### Serial Number Tracking Flow

```bash
# 1. Create Serial Numbers
POST /api/v1/tracking/serial-numbers
{
  "serial_no": "SN-2026-001",
  "item_id": "{item_id}",
  "warehouse_id": "{warehouse_id}",
  "purchase_date": "2026-01-17T00:00:00Z",
  "purchase_rate": 1000.00,
  "warranty_period": 365
}

# 2. Use in Stock Entry
POST /api/v1/stock-transactions/stock-entries
{
  "stock_entry_type": "material_receipt",
  "to_warehouse_id": "{warehouse_id}",
  "items": [
    {
      "item_id": "{item_id}",
      "target_warehouse_id": "{warehouse_id}",
      "qty": 1,
      "uom": "Nos",
      "serial_nos": ["SN-2026-001"],
      "valuation_rate": 1000.00
    }
  ]
}

# 3. Track on Delivery
PATCH /api/v1/tracking/serial-numbers/{serial_id}
{
  "status": "delivered",
  "customer_id": "{customer_id}",
  "delivery_date": "2026-01-17T00:00:00Z"
}
```

---

## Common Queries

### Get Stock Balance for an Item
```bash
GET /api/v1/inventory/items/{item_id}
# Returns item details including current stock levels
```

### Get All Items in a Warehouse
```bash
GET /api/v1/stock-transactions/stock-entries?to_warehouse_id={warehouse_id}&stock_entry_type=material_receipt
# Filter stock entries by warehouse
```

### Get Expired Batches
```bash
GET /api/v1/tracking/batches?status=expired
```

### Get Items Below Reorder Level
```bash
GET /api/v1/inventory/items?enable_auto_reorder=true
# Then filter client-side based on current stock vs reorder_level
```

### Get Pending Quality Inspections
```bash
GET /api/v1/tracking/quality-inspections?status=pending
```

### Get Available Serial Numbers
```bash
GET /api/v1/tracking/serial-numbers?status=available&warehouse_id={warehouse_id}
```

---

## Permission Matrix

| Resource | List | Create | Read | Update | Delete |
|----------|------|--------|------|--------|--------|
| Item Groups | `inventory:item_group:list` | `inventory:item_group:create` | `inventory:item_group:read` | `inventory:item_group:update` | `inventory:item_group:delete` |
| Items | `inventory:item:list` | `inventory:item:create` | `inventory:item:read` | `inventory:item:update` | `inventory:item:delete` |
| Warehouses | `inventory:warehouse:list` | `inventory:warehouse:create` | `inventory:warehouse:read` | `inventory:warehouse:update` | `inventory:warehouse:delete` |
| Put-Away Rules | `inventory:putaway:list` | `inventory:putaway:create` | - | `inventory:putaway:update` | - |
| Pick Lists | `inventory:picklist:list` | `inventory:picklist:create` | `inventory:picklist:read` | `inventory:picklist:update` | - |
| Stock Entries | `inventory:stock_entry:list` | `inventory:stock_entry:create` | `inventory:stock_entry:read` | `inventory:stock_entry:update` | - |
| Reconciliations | `inventory:reconciliation:list` | `inventory:reconciliation:create` | `inventory:reconciliation:read` | `inventory:reconciliation:update` | - |
| Delivery Notes | `inventory:delivery_note:list` | `inventory:delivery_note:create` | `inventory:delivery_note:read` | `inventory:delivery_note:update` | - |
| Purchase Receipts | `inventory:purchase_receipt:list` | `inventory:purchase_receipt:create` | `inventory:purchase_receipt:read` | `inventory:purchase_receipt:update` | - |
| Landed Costs | - | `inventory:landed_cost:create` | - | - | - |
| Batches | `inventory:batch:list` | `inventory:batch:create` | - | `inventory:batch:update` | - |
| Serial Numbers | `inventory:serial:list` | `inventory:serial:create` | - | `inventory:serial:update` | - |
| QI Templates | `inventory:quality_template:list` | `inventory:quality_template:create` | - | - | - |
| Quality Inspections | `inventory:quality_inspection:list` | `inventory:quality_inspection:create` | - | `inventory:quality_inspection:update` | - |
| Stock Settings | `inventory:settings:read` | `inventory:settings:create` | - | `inventory:settings:update` | - |

---

## Status Transitions

### Stock Entry / Reconciliation
```
draft → submitted → cancelled
```

### Delivery Note / Purchase Receipt
```
draft → submitted → completed
                 → cancelled
                 → returned
```

### Quality Inspection
```
pending → accepted
        → rejected
```

### Pick List
```
draft → submitted → completed
                  → cancelled
```

### Batch
```
active → expired
       → recalled
```

---

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `DUPLICATE_ITEM_CODE` | Item code already exists | 409 |
| `DUPLICATE_BARCODE` | Barcode already exists | 409 |
| `DUPLICATE_SERIAL_NO` | Serial number already exists | 409 |
| `ITEM_NOT_FOUND` | Item not found | 404 |
| `WAREHOUSE_NOT_FOUND` | Warehouse not found | 404 |
| `PARENT_NOT_FOUND` | Parent item/group not found | 404 |
| `INVALID_VARIANT` | Parent item doesn't support variants | 400 |
| `INVALID_STATUS_TRANSITION` | Cannot change status | 400 |
| `WAREHOUSE_REQUIRED` | Warehouse required for this operation | 400 |
| `SETTINGS_ALREADY_EXIST` | Stock settings already configured | 409 |

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/horizon_erp

# Service
SERVICE_NAME=inventory
SERVICE_PORT=8003

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
```

---

## Testing

### Unit Tests
```bash
pytest tests/inventory/test_items.py
pytest tests/inventory/test_warehouses.py
pytest tests/inventory/test_stock_entries.py
```

### Integration Tests
```bash
pytest tests/inventory/integration/
```

### Load Tests
```bash
locust -f tests/inventory/locustfile.py
```

---

## Troubleshooting

### Issue: "Item code already exists"
**Solution**: Check for existing items with the same code. Use PATCH to update instead of POST.

### Issue: "Cannot modify submitted stock entry"
**Solution**: Submitted entries are immutable. Create a new entry or cancel and recreate.

### Issue: "Warehouse not found"
**Solution**: Ensure warehouse exists and is not soft-deleted. Check `deleted_at` field.

### Issue: "Permission denied"
**Solution**: Verify user has required permission in JWT token claims.

### Issue: "Negative stock not allowed"
**Solution**: Enable in Stock Settings or ensure sufficient stock before issuing.

---

## Best Practices

1. **Always set stock settings first** before creating transactions
2. **Use hierarchical structures** for item groups and warehouses
3. **Enable quality inspection** for critical items
4. **Configure auto-reorder** for frequently used items
5. **Use batch tracking** for items with expiry dates
6. **Use serial tracking** for high-value items with warranty
7. **Apply put-away rules** for efficient warehouse management
8. **Set tolerances** to handle minor variances
9. **Use pick lists** for organized order fulfillment
10. **Submit documents** to make them immutable and trigger accounting

---

## Support

For issues or questions:
1. Check API documentation: `/docs`
2. Review implementation summary: `IMPLEMENTATION_SUMMARY.md`
3. Check detailed API docs: `INVENTORY_API_DOCUMENTATION.md`
4. Contact: dev@horizonerp.com
