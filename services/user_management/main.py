"""User Management Service FastAPI application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import init_db
from shared.middleware.tenant import TenantMiddleware
from shared.middleware.auth import AuthMiddleware
from shared.middleware.audit import AuditMiddleware
from services.user_management.api.v1 import router as v1_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting User Management Service...")
    await init_db()
    logger.info("User Management Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down User Management Service...")


# Create FastAPI app
app = FastAPI(
    title="Horizon Sync ERP - User Management Service",
    description="User, Organization, Role, Team, and Subscription management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware (order matters - last added is first executed)
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

# Include API routers
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "user_management",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "services.user_management.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
