"""API v1 router for inventory service."""
from fastapi import APIRouter
from services.inventory.api.v1 import (
    products,
    stock,
    warehouses,
    items,
    warehouse_management,
    stock_transactions,
    delivery_purchase,
    batch_serial_quality,
    settings
)

router = APIRouter()

# Legacy endpoints (keeping for backward compatibility)
router.include_router(products.router, prefix="/products", tags=["Products (Legacy)"])
router.include_router(stock.router, prefix="/stock", tags=["Stock (Legacy)"])
router.include_router(warehouses.router, prefix="/warehouses-legacy", tags=["Warehouses (Legacy)"])

# New comprehensive inventory management endpoints
router.include_router(items.router, prefix="/inventory", tags=["Items & Item Groups"])
router.include_router(warehouse_management.router, prefix="/warehouse", tags=["Warehouse Management"])
router.include_router(stock_transactions.router, prefix="/stock-transactions", tags=["Stock Transactions"])
router.include_router(delivery_purchase.router, prefix="/transactions", tags=["Delivery & Purchase"])
router.include_router(batch_serial_quality.router, prefix="/tracking", tags=["Batch, Serial & Quality"])
router.include_router(settings.router, prefix="/stock-settings", tags=["Stock Settings"])
