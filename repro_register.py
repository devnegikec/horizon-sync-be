import asyncio
import httpx
import json

async def register():
    url = "http://localhost:8001/api/v1/auth/register"
    payload = {
        "email": "testuser_repro@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "organization_name": "Test Org"
    }
    
    print(f"Calling {url} with payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(register())
