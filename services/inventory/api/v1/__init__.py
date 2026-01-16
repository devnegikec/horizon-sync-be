"""Inventory API v1 router."""
from fastapi import APIRouter
from services.inventory.api.v1.products import router as products_router
from services.inventory.api.v1.warehouses import router as warehouses_router
from services.inventory.api.v1.stock import router as stock_router

router = APIRouter()
router.include_router(products_router, prefix="/products", tags=["Products"])
router.include_router(warehouses_router, prefix="/warehouses", tags=["Warehouses"])
router.include_router(stock_router, prefix="/inventory", tags=["Stock"])
