
import os
import re

def verify_nginx_cors():
    print("Verifying nginx/nginx.conf CORS configuration...")
    with open("nginx/nginx.conf", "r") as f:
        content = f.read()
    
    required_headers = [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ]
    
    all_passed = True
    for header in required_headers:
        if header in content:
            print(f"  [PASS] Found {header}")
        else:
            print(f"  [FAIL] Missing {header}")
            all_passed = False
            
    if "if ($request_method = 'OPTIONS')" in content and "return 204;" in content:
        print("  [PASS] Found OPTIONS preflight handling")
    else:
        print("  [FAIL] Missing OPTIONS preflight handling")
        all_passed = False
        
    return all_passed

def verify_shared_config_cors():
    print("\nVerifying shared/config.py CORS configuration...")
    with open("shared/config.py", "r") as f:
        content = f.read()
    
    if 'CORS_ORIGINS: List[str] = ["*"]' in content:
        print("  [PASS] CORS_ORIGINS set to ['*']")
        return True
    else:
        print("  [FAIL] CORS_ORIGINS NOT set to ['*']")
        # Show what it is
        match = re.search(r'CORS_ORIGINS: List\[str\] = (.*)', content)
        if match:
            print(f"         Current value: {match.group(1)}")
        return False

if __name__ == "__main__":
    nginx_ok = verify_nginx_cors()
    config_ok = verify_shared_config_cors()
    
    if nginx_ok and config_ok:
        print("\nOVERALL CORS VERIFICATION: PASSED")
        exit(0)
    else:
        print("\nOVERALL CORS VERIFICATION: FAILED")
        exit(1)
