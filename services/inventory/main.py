"""Inventory Service FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings
from shared.database import init_db
from shared.middleware.tenant import TenantMiddleware
from shared.middleware.auth import AuthMiddleware
from services.inventory.api.v1 import router as v1_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Inventory Service...")
    await init_db()
    yield
    logger.info("Shutting down Inventory Service...")

app = FastAPI(title="Horizon Sync ERP - Inventory Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory", "version": "1.0.0"}
