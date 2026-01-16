"""User Management API v1 router."""
from fastapi import APIRouter

from services.user_management.api.v1.organizations import router as org_router
from services.user_management.api.v1.users import router as users_router
from services.user_management.api.v1.roles import router as roles_router
from services.user_management.api.v1.permissions import router as permissions_router
from services.user_management.api.v1.teams import router as teams_router
from services.user_management.api.v1.subscriptions import router as subscriptions_router
from services.user_management.api.v1.audit import router as audit_router

router = APIRouter()

# Include sub-routers
router.include_router(org_router, prefix="/organizations", tags=["Organizations"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(roles_router, prefix="/roles", tags=["Roles"])
router.include_router(permissions_router, prefix="/permissions", tags=["Permissions"])
router.include_router(teams_router, prefix="/teams", tags=["Teams"])
router.include_router(subscriptions_router, prefix="/subscriptions", tags=["Subscriptions"])
router.include_router(audit_router, prefix="/audit-logs", tags=["Audit"])
