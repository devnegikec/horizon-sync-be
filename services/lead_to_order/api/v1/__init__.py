"""Lead-to-Order API v1 router."""
from fastapi import APIRouter

from services.lead_to_order.api.v1.leads import router as leads_router
from services.lead_to_order.api.v1.contacts import router as contacts_router
from services.lead_to_order.api.v1.deals import router as deals_router
from services.lead_to_order.api.v1.quotes import router as quotes_router
from services.lead_to_order.api.v1.orders import router as orders_router

router = APIRouter()

router.include_router(leads_router, prefix="/leads", tags=["Leads"])
router.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])
router.include_router(deals_router, prefix="/deals", tags=["Deals"])
router.include_router(quotes_router, prefix="/quotes", tags=["Quotes"])
router.include_router(orders_router, prefix="/orders", tags=["Orders"])
