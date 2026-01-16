"""Support Ticket API v1 router."""
from fastapi import APIRouter
from services.support_ticket.api.v1.tickets import router as tickets_router

router = APIRouter()
router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
