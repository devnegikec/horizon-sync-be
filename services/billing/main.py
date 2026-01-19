from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.exceptions.handlers import setup_exception_handlers

# Import routers
from services.billing.api.v1 import (
    customers, suppliers, invoices, payments, accounting
)

app = FastAPI(
    title="Horizon Sync - Billing & Accounting Service",
    description="Microservice for managing customers, suppliers, invoicing, and accounting.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
setup_exception_handlers(app)

@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "service": "billing-service",
        "version": "1.0.0"
    }

# Include Routers
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["Invoices"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(accounting.router, prefix="/api/v1/accounting", tags=["Accounting"])
