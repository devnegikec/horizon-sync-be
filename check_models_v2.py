
import sys
import os
import traceback

# Add the project root to sys.path
sys.path.append(os.getcwd())

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
print("Attempting to import models...")

try:
    print("Importing shared.database.base...")
    from shared.database.base import Base
    print("Base imported successfully")
    
    print("Importing shared.models.organization...")
    from shared.models.organization import Organization
    print("Organization imported successfully")
    
    print("Importing shared.models.user...")
    from shared.models.user import User
    print("User imported successfully")
    
    print("Importing shared.models.role...")
    from shared.models.role import Role
    print("Role imported successfully")
    
    print("Importing shared.models.auth...")
    from shared.models.auth import Invitation
    print("Invitation (auth) imported successfully")
    
    print("Importing shared.models.audit...")
    from shared.models.audit import AuditLog
    print("AuditLog imported successfully")
    
    print("Importing shared.models.subscription...")
    from shared.models.subscription import Subscription
    print("Subscription imported successfully")

    print("Testing intentional failure...")
    try:
        class FailModel(Base):
            __tablename__ = "fail_model"
            id = Column(UUID(as_uuid=True), primary_key=True)
            metadata = Column(String)
        print("FailModel declared (this should NOT happen!)")
    except Exception as e:
        print(f"Caught expected failure: {e}")

    print("Importing service models...")
    from services.inventory.models.product import Product
    print("Product (inventory) imported successfully")
    
    from services.lead_to_order.models.lead import Lead
    print("Lead (lead_to_order) imported successfully")
    
    from services.support_ticket.models.ticket import Ticket
    print("Ticket (support_ticket) imported successfully")

    print("Configuring mappers...")
    from sqlalchemy.orm import configure_mappers
    configure_mappers()
    print("Mappers configured successfully!")

    print("\nAll models imported and configured successfully!")

except Exception as e:
    print(f"\nCaught Exception: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
