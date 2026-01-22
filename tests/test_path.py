import sys
import os

def test_print_path():
    print(f"\nCWD: {os.getcwd()}")
    print(f"PYTHONPATH env: {os.environ.get('PYTHONPATH')}")
    print("sys.path:")
    for p in sys.path:
        print(f"  {p}")
    
    try:
        import services
        print(f"services imported from: {services.__file__}")
    except ImportError as e:
        print(f"Failed to import services: {e}")

    try:
        from services.user_management.main import app
        print("Successfully imported user_management.main")
    except ImportError as e:
        print(f"Failed to import user_management.main: {e}")
