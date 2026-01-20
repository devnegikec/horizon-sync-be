import json
import os
import sys
from fastapi.openapi.utils import get_openapi

sys.path.append(os.getcwd())

services = [
    ("auth", "services.auth.main"),
    ("billing", "services.billing.main"),
    ("inventory", "services.inventory.main"),
    ("lead-to-order", "services.lead_to_order.main"),
    ("support-ticket", "services.support_ticket.main"),
    ("user-management", "services.user_management.main"),
]

output_dir = "api_contracts"
os.makedirs(output_dir, exist_ok=True)

for name, module_path in services:
    try:
        module = __import__(module_path, fromlist=["app"])
        app = getattr(module, "app")
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        
        service_dir = os.path.join(output_dir, f"{name}-service")
        os.makedirs(service_dir, exist_ok=True)
        
        with open(os.path.join(service_dir, "openapi.json"), "w") as f:
            json.dump(openapi_schema, f, indent=2)
            
        print(f"Generated openapi.json for {name}")
    except Exception as e:
        print(f"Failed to generate openapi.json for {name}: {e}")
        import traceback
        traceback.print_exc()
