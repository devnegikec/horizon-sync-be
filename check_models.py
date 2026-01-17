
import sys
import os
sys.path.append(os.getcwd())

try:
    from shared.database.base import Base
    from shared.models import organization, user, role, team, subscription, audit, auth
    print("Shared models imported successfully")
    
    from services.support_ticket.models import ticket, comment
    print("Support ticket models imported successfully")
    
    from services.lead_to_order.models import lead, deal, contact, quote, order
    print("Lead to order models imported successfully")
    
    from services.inventory.models import product, stock, warehouse
    print("Inventory models imported successfully")
    
except Exception as e:
    print(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()
