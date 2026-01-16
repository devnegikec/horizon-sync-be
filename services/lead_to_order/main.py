"""Lead-to-Order Service FastAPI application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import init_db
from shared.middleware.tenant import TenantMiddleware
from shared.middleware.auth import AuthMiddleware
from shared.middleware.audit import AuditMiddleware
from services.lead_to_order.api.v1 import router as v1_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Lead-to-Order Service...")
    await init_db()
    logger.info("Lead-to-Order Service started successfully")
    
    yield
    
    logger.info("Shutting down Lead-to-Order Service...")


app = FastAPI(
    title="Horizon Sync ERP - Lead-to-Order Service",
    description="Lead, Deal, Quote, and Order management for CRM",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lead_to_order",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.lead_to_order.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
