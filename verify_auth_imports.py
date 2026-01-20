import sys
import os

sys.path.append(os.getcwd())

try:
    from services.auth.main import app
    print("Successfully imported services.auth.main")
    from services.auth.services.auth_service import AuthService
    print("Successfully imported AuthService")
except Exception as e:
    print(f"Failed to import: {e}")
    import traceback
    traceback.print_exc()
