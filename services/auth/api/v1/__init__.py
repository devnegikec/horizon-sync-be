"""Auth API v1 router."""
from fastapi import APIRouter

from services.auth.api.v1.auth import router as auth_router
from services.auth.api.v1.mfa import router as mfa_router
from services.auth.api.v1.sessions import router as sessions_router

router = APIRouter(tags=["Auth"])

# Include sub-routers
router.include_router(auth_router, prefix="/auth")
router.include_router(mfa_router, prefix="/auth/mfa")
router.include_router(sessions_router, prefix="/auth/sessions")
