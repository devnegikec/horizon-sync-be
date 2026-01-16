"""Auth Service FastAPI application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import init_db
from shared.middleware.audit import AuditMiddleware
from services.auth.api.v1 import router as v1_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Auth Service...")
    await init_db()
    logger.info("Auth Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Auth Service...")


# Create FastAPI app
app = FastAPI(
    title="Horizon Sync ERP - Auth Service",
    description="Authentication and authorization service for Horizon Sync ERP",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add audit middleware
app.add_middleware(AuditMiddleware)

# Include API routers
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "auth",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "services.auth.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
