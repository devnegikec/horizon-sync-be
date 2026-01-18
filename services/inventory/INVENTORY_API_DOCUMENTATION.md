# Inventory Management System - REST API Documentation

## Overview

This document provides comprehensive documentation for the Inventory Management System REST APIs, built following ERPNext patterns and best practices. The system supports multi-tenancy, role-based access control, and is production-ready for SaaS deployment.

## Table of Contents

1. [Master Data Management](#1-master-data-management)
2. [Warehouse Management](#2-warehouse-management)
3. [Stock Transactions](#3-stock-transactions)
4. [Delivery & Purchase](#4-delivery--purchase)
5. [Batch, Serial & Quality](#5-batch-serial--quality)
6. [Stock Settings](#6-stock-settings)

---

## 1. Master Data Management

### Item Groups

Hierarchical classification for items.

#### Endpoints

- **GET** `/api/v1/inventory/item-groups` - List all item groups
  - Query params: `page`, `page_size`, `search`, `parent_id`, `is_active`
  - Permission: `inventory:item_group:list`

- **POST** `/api/v1/inventory/item-groups` - Create item group
  - Permission: `inventory:item_group:create`
  - Body:
    ```json
    {
      "name": "Raw Materials",
      "code": "RM",
      "description": "Raw materials for manufacturing",
      "parent_id": "uuid-or-null",
      "default_valuation_method": "fifo",
      "default_uom": "Kg"
    }
    ```

- **GET** `/api/v1/inventory/item-groups/{group_id}` - Get item group by ID
  - Permission: `inventory:item_group:read`

- **PATCH** `/api/v1/inventory/item-groups/{group_id}` - Update item group
  - Permission: `inventory:item_group:update`

- **DELETE** `/api/v1/inventory/item-groups/{group_id}` - Soft delete item group
  - Permission: `inventory:item_group:delete`

### Items

Core item master with support for variants, batches, serials, and reordering.

#### Endpoints

- **GET** `/api/v1/inventory/items` - List all items
  - Query params: `page`, `page_size`, `search`, `item_group_id`, `item_type`, `status`, `has_variants`
  - Permission: `inventory:item:list`

- **POST** `/api/v1/inventory/items` - Create item
  - Permission: `inventory:item:create`
  - Body:
    ```json
    {
      "item_code": "ITEM-001",
      "item_name": "Polyester Sheet",
      "description": "High quality polyester sheet",
      "item_group_id": "uuid",
      "item_type": "stock",
      "uom": "Nos",
      "maintain_stock": true,
      "valuation_method": "fifo",
      "allow_negative_stock": false,
      "has_variants": false,
      "has_batch_no": false,
      "has_serial_no": false,
      "standard_rate": 100.00,
      "enable_auto_reorder": true,
      "reorder_level": 50,
      "reorder_qty": 200,
      "inspection_required_before_purchase": false,
      "inspection_required_before_delivery": false,
      "barcode": "1234567890"
    }
    ```

- **GET** `/api/v1/inventory/items/{item_id}` - Get item by ID
  - Permission: `inventory:item:read`

- **PATCH** `/api/v1/inventory/items/{item_id}` - Update item
  - Permission: `inventory:item:update`

- **DELETE** `/api/v1/inventory/items/{item_id}` - Soft delete item
  - Permission: `inventory:item:delete`

---

## 2. Warehouse Management

### Warehouses

Hierarchical warehouse structure with capacity management.

#### Endpoints

- **GET** `/api/v1/warehouse/warehouses` - List all warehouses
  - Query params: `page`, `page_size`, `search`, `warehouse_type`, `is_active`, `parent_warehouse_id`
  - Permission: `inventory:warehouse:list`

- **POST** `/api/v1/warehouse/warehouses` - Create warehouse
  - Permission: `inventory:warehouse:create`
  - Body:
    ```json
    {
      "name": "Eastern Raw Materials",
      "code": "WH-EAST-RM",
      "description": "Eastern warehouse for raw materials",
      "parent_warehouse_id": "uuid-or-null",
      "warehouse_type": "standard",
      "address_line1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA",
      "contact_name": "John Doe",
      "contact_phone": "+1234567890",
      "contact_email": "john@example.com",
      "total_capacity": 10000,
      "capacity_uom": "units",
      "is_default": false
    }
    ```

- **GET** `/api/v1/warehouse/warehouses/{warehouse_id}` - Get warehouse by ID
  - Permission: `inventory:warehouse:read`

- **PATCH** `/api/v1/warehouse/warehouses/{warehouse_id}` - Update warehouse
  - Permission: `inventory:warehouse:update`

- **DELETE** `/api/v1/warehouse/warehouses/{warehouse_id}` - Soft delete warehouse
  - Permission: `inventory:warehouse:delete`

### Put-Away Rules

Rules for automatic warehouse assignment based on capacity and priority.

#### Endpoints

- **GET** `/api/v1/warehouse/put-away-rules` - List all put-away rules
  - Query params: `page`, `page_size`, `warehouse_id`, `item_id`, `is_active`
  - Permission: `inventory:putaway:list`

- **POST** `/api/v1/warehouse/put-away-rules` - Create put-away rule
  - Permission: `inventory:putaway:create`
  - Body:
    ```json
    {
      "name": "UPI-003 to Warehouse 1",
      "item_id": "uuid",
      "warehouse_id": "uuid",
      "capacity": 600,
      "priority": 1,
      "min_qty": 0,
      "max_qty": 1000
    }
    ```

- **PATCH** `/api/v1/warehouse/put-away-rules/{rule_id}` - Update put-away rule
  - Permission: `inventory:putaway:update`

### Pick Lists

Order fulfillment pick lists from sales/work orders.

#### Endpoints

- **GET** `/api/v1/warehouse/pick-lists` - List all pick lists
  - Query params: `page`, `page_size`, `status`, `warehouse_id`, `assigned_to`
  - Permission: `inventory:picklist:list`

- **POST** `/api/v1/warehouse/pick-lists` - Create pick list
  - Permission: `inventory:picklist:create`
  - Body:
    ```json
    {
      "reference_type": "sales_order",
      "reference_id": "uuid",
      "warehouse_id": "uuid",
      "pick_date": "2026-01-17T10:00:00Z",
      "assigned_to": "uuid",
      "notes": "Urgent order",
      "items": [
        {
          "item_id": "uuid",
          "warehouse_id": "uuid",
          "qty_to_pick": 10,
          "batch_no": "BATCH-001",
          "bin_location": "A-1-2"
        }
      ]
    }
    ```

- **GET** `/api/v1/warehouse/pick-lists/{pick_list_id}` - Get pick list with items
  - Permission: `inventory:picklist:read`

- **PATCH** `/api/v1/warehouse/pick-lists/{pick_list_id}` - Update pick list status
  - Permission: `inventory:picklist:update`

- **PATCH** `/api/v1/warehouse/pick-lists/{pick_list_id}/items/{item_id}` - Update picked quantity
  - Permission: `inventory:picklist:update`

---

## 3. Stock Transactions

### Stock Entries

Material movements (receipts, issues, transfers, manufacturing).

#### Endpoints

- **GET** `/api/v1/stock-transactions/stock-entries` - List all stock entries
  - Query params: `page`, `page_size`, `stock_entry_type`, `status`, `from_warehouse_id`, `to_warehouse_id`, `from_date`, `to_date`
  - Permission: `inventory:stock_entry:list`

- **POST** `/api/v1/stock-transactions/stock-entries` - Create stock entry
  - Permission: `inventory:stock_entry:create`
  - Body:
    ```json
    {
      "stock_entry_type": "material_receipt",
      "to_warehouse_id": "uuid",
      "posting_date": "2026-01-17T10:00:00Z",
      "posting_time": "10:00",
      "remarks": "Initial stock",
      "items": [
        {
          "item_id": "uuid",
          "target_warehouse_id": "uuid",
          "qty": 100,
          "uom": "Nos",
          "basic_rate": 50.00,
          "valuation_rate": 50.00
        }
      ]
    }
    ```

- **GET** `/api/v1/stock-transactions/stock-entries/{entry_id}` - Get stock entry with items
  - Permission: `inventory:stock_entry:read`

- **PATCH** `/api/v1/stock-transactions/stock-entries/{entry_id}` - Update stock entry (status)
  - Permission: `inventory:stock_entry:update`

### Stock Reconciliation

Physical count adjustments and opening stock.

#### Endpoints

- **GET** `/api/v1/stock-transactions/stock-reconciliations` - List all reconciliations
  - Query params: `page`, `page_size`, `purpose`, `status`, `from_date`, `to_date`
  - Permission: `inventory:reconciliation:list`

- **POST** `/api/v1/stock-transactions/stock-reconciliations` - Create reconciliation
  - Permission: `inventory:reconciliation:create`
  - Body:
    ```json
    {
      "purpose": "opening_stock",
      "posting_date": "2026-01-01T00:00:00Z",
      "remarks": "Opening stock for FY 2026",
      "items": [
        {
          "item_id": "uuid",
          "warehouse_id": "uuid",
          "qty": 500,
          "valuation_rate": 45.00
        }
      ]
    }
    ```

- **GET** `/api/v1/stock-transactions/stock-reconciliations/{reconciliation_id}` - Get reconciliation
  - Permission: `inventory:reconciliation:read`

- **PATCH** `/api/v1/stock-transactions/stock-reconciliations/{reconciliation_id}` - Update reconciliation
  - Permission: `inventory:reconciliation:update`

---

## 4. Delivery & Purchase

### Delivery Notes

Customer deliveries with tolerance support.

#### Endpoints

- **GET** `/api/v1/transactions/delivery-notes` - List all delivery notes
  - Query params: `page`, `page_size`, `status`, `customer_id`, `from_date`, `to_date`
  - Permission: `inventory:delivery_note:list`

- **POST** `/api/v1/transactions/delivery-notes` - Create delivery note
  - Permission: `inventory:delivery_note:create`
  - Body:
    ```json
    {
      "customer_id": "uuid",
      "customer_name": "ABC Corp",
      "sales_order_id": "uuid",
      "warehouse_id": "uuid",
      "posting_date": "2026-01-17T10:00:00Z",
      "delivery_date": "2026-01-18T10:00:00Z",
      "shipping_address_line1": "456 Customer St",
      "shipping_city": "Boston",
      "shipping_state": "MA",
      "shipping_country": "USA",
      "tracking_number": "TRACK123",
      "carrier": "FedEx",
      "over_delivery_percentage": 10,
      "items": [
        {
          "item_id": "uuid",
          "warehouse_id": "uuid",
          "qty": 50,
          "uom": "Nos",
          "rate": 100.00
        }
      ]
    }
    ```

- **GET** `/api/v1/transactions/delivery-notes/{delivery_note_id}` - Get delivery note
  - Permission: `inventory:delivery_note:read`

- **PATCH** `/api/v1/transactions/delivery-notes/{delivery_note_id}` - Update delivery note
  - Permission: `inventory:delivery_note:update`

### Purchase Receipts

Supplier deliveries with put-away rule support.

#### Endpoints

- **GET** `/api/v1/transactions/purchase-receipts` - List all purchase receipts
  - Query params: `page`, `page_size`, `status`, `supplier_id`, `from_date`, `to_date`
  - Permission: `inventory:purchase_receipt:list`

- **POST** `/api/v1/transactions/purchase-receipts` - Create purchase receipt
  - Permission: `inventory:purchase_receipt:create`
  - Body:
    ```json
    {
      "supplier_id": "uuid",
      "supplier_name": "XYZ Suppliers",
      "purchase_order_id": "uuid",
      "warehouse_id": "uuid",
      "posting_date": "2026-01-17T10:00:00Z",
      "supplier_delivery_note": "DN-123",
      "supplier_invoice_no": "INV-456",
      "over_receipt_percentage": 5,
      "apply_putaway_rule": true,
      "items": [
        {
          "item_id": "uuid",
          "warehouse_id": "uuid",
          "qty": 200,
          "uom": "Kg",
          "rate": 25.00
        }
      ]
    }
    ```

- **GET** `/api/v1/transactions/purchase-receipts/{receipt_id}` - Get purchase receipt
  - Permission: `inventory:purchase_receipt:read`

- **PATCH** `/api/v1/transactions/purchase-receipts/{receipt_id}` - Update purchase receipt
  - Permission: `inventory:purchase_receipt:update`

### Landed Cost Vouchers

Additional costs (freight, customs) distribution.

#### Endpoints

- **POST** `/api/v1/transactions/landed-cost-vouchers` - Create landed cost voucher
  - Permission: `inventory:landed_cost:create`
  - Body:
    ```json
    {
      "posting_date": "2026-01-17T10:00:00Z",
      "distribute_charges_based_on": "qty",
      "purchase_receipt_ids": ["uuid1", "uuid2"],
      "taxes_and_charges": [
        {
          "expense_account_id": "uuid",
          "description": "Freight charges",
          "amount": 500.00
        },
        {
          "expense_account_id": "uuid",
          "description": "Customs duty",
          "amount": 300.00
        }
      ],
      "remarks": "Import charges for shipment #123"
    }
    ```

---

## 5. Batch, Serial & Quality

### Batches

Batch tracking with expiry dates.

#### Endpoints

- **GET** `/api/v1/tracking/batches` - List all batches
  - Query params: `page`, `page_size`, `item_id`, `status`, `search`
  - Permission: `inventory:batch:list`

- **POST** `/api/v1/tracking/batches` - Create batch
  - Permission: `inventory:batch:create`
  - Body:
    ```json
    {
      "batch_no": "BATCH-2026-001",
      "item_id": "uuid",
      "manufacturing_date": "2026-01-01T00:00:00Z",
      "expiry_date": "2027-01-01T00:00:00Z",
      "supplier_id": "uuid",
      "supplier_batch_no": "SUP-BATCH-123"
    }
    ```

- **PATCH** `/api/v1/tracking/batches/{batch_id}` - Update batch
  - Permission: `inventory:batch:update`

### Serial Numbers

Serial number tracking with warranty.

#### Endpoints

- **GET** `/api/v1/tracking/serial-numbers` - List all serial numbers
  - Query params: `page`, `page_size`, `item_id`, `warehouse_id`, `status`, `search`
  - Permission: `inventory:serial:list`

- **POST** `/api/v1/tracking/serial-numbers` - Create serial number
  - Permission: `inventory:serial:create`
  - Body:
    ```json
    {
      "serial_no": "SN-2026-001",
      "item_id": "uuid",
      "warehouse_id": "uuid",
      "purchase_date": "2026-01-17T00:00:00Z",
      "purchase_rate": 1000.00,
      "supplier_id": "uuid",
      "warranty_period": 365,
      "batch_no": "BATCH-2026-001"
    }
    ```

- **PATCH** `/api/v1/tracking/serial-numbers/{serial_id}` - Update serial number
  - Permission: `inventory:serial:update`

### Quality Inspection Templates

Templates with parameters for quality checks.

#### Endpoints

- **GET** `/api/v1/tracking/quality-inspection-templates` - List all templates
  - Query params: `page`, `page_size`, `is_active`
  - Permission: `inventory:quality_template:list`

- **POST** `/api/v1/tracking/quality-inspection-templates` - Create template
  - Permission: `inventory:quality_template:create`
  - Body:
    ```json
    {
      "template_name": "Raw Material Inspection",
      "description": "Standard inspection for raw materials",
      "item_group_id": "uuid",
      "parameters": [
        {
          "parameter_name": "Weight",
          "reading_type": "numeric",
          "min_value": 95.0,
          "max_value": 105.0,
          "non_conformance_action": "stop",
          "sequence": 1
        },
        {
          "parameter_name": "Visual Inspection",
          "reading_type": "pass_fail",
          "acceptance_criteria": "No visible defects",
          "non_conformance_action": "warn",
          "sequence": 2
        }
      ]
    }
    ```

### Quality Inspections

Actual inspection records.

#### Endpoints

- **GET** `/api/v1/tracking/quality-inspections` - List all inspections
  - Query params: `page`, `page_size`, `item_id`, `status`, `inspection_type`
  - Permission: `inventory:quality_inspection:list`

- **POST** `/api/v1/tracking/quality-inspections` - Create inspection
  - Permission: `inventory:quality_inspection:create`
  - Body:
    ```json
    {
      "item_id": "uuid",
      "template_id": "uuid",
      "inspection_type": "incoming",
      "reference_type": "purchase_receipt",
      "reference_id": "uuid",
      "batch_no": "BATCH-2026-001",
      "sample_size": 10,
      "inspected_by": "uuid",
      "inspection_date": "2026-01-17T10:00:00Z",
      "readings": [
        {
          "parameter_name": "Weight",
          "numeric_value": 98.5,
          "status": "accepted"
        },
        {
          "parameter_name": "Visual Inspection",
          "reading_value": "Pass",
          "status": "accepted"
        }
      ]
    }
    ```

- **PATCH** `/api/v1/tracking/quality-inspections/{inspection_id}` - Update inspection
  - Permission: `inventory:quality_inspection:update`

---

## 6. Stock Settings

Global configuration for inventory management.

#### Endpoints

- **GET** `/api/v1/stock-settings/settings` - Get stock settings
  - Permission: `inventory:settings:read`

- **POST** `/api/v1/stock-settings/settings` - Create stock settings
  - Permission: `inventory:settings:create`
  - Body:
    ```json
    {
      "item_naming_by": "naming_series",
      "item_naming_series": "ITEM-.####",
      "stock_entry_naming_series": "STE-.######",
      "delivery_note_naming_series": "DN-.######",
      "purchase_receipt_naming_series": "PR-.######",
      "default_warehouse_id": "uuid",
      "allow_negative_stock": false,
      "over_delivery_receipt_allowance": 10,
      "over_billing_allowance": 5,
      "auto_indent": true,
      "auto_indent_notification": ["Stock Manager", "Purchase Manager"],
      "default_valuation_method": "fifo",
      "auto_create_serial_no": false,
      "stock_frozen_upto_days": 0,
      "show_barcode_field": true
    }
    ```

- **PATCH** `/api/v1/stock-settings/settings` - Update stock settings
  - Permission: `inventory:settings:update`

---

## Common Response Formats

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": null
}
```

### Error Response
```json
{
  "success": false,
  "error": "Validation error",
  "detail": "Item code already exists",
  "code": "DUPLICATE_ITEM_CODE"
}
```

---

## Authentication & Authorization

All endpoints require:
1. **Authentication**: Valid JWT token in `Authorization: Bearer <token>` header
2. **Tenant Context**: Organization ID extracted from token or header
3. **Permissions**: Specific permission for each operation (listed in endpoint descriptions)

---

## Best Practices

1. **Naming Series**: Configure in Stock Settings for auto-generated document numbers
2. **Tolerances**: Set over-delivery/receipt allowances to handle minor variances
3. **Quality Inspection**: Enable on items requiring quality checks before purchase/delivery
4. **Auto-Reordering**: Configure reorder levels and enable auto-indent for automatic material requests
5. **Batch/Serial**: Enable on items requiring traceability
6. **Put-Away Rules**: Define for automatic warehouse assignment based on capacity
7. **Hierarchical Structures**: Use parent-child relationships for item groups and warehouses
8. **Soft Deletes**: All deletions are soft deletes (deleted_at timestamp)

---

## Status Workflows

### Stock Entry / Reconciliation
- `draft` → `submitted` → `cancelled`

### Delivery Note / Purchase Receipt
- `draft` → `submitted` → `completed` / `cancelled` / `returned`

### Quality Inspection
- `pending` → `accepted` / `rejected`

### Pick List
- `draft` → `submitted` → `completed` / `cancelled`

---

## Notes

- All dates are in ISO 8601 format (UTC)
- All monetary values are in decimal format with 2 decimal places
- All quantities support 3 decimal places
- UUIDs are used for all entity IDs
- Multi-tenancy is enforced at the database level via `organization_id`
