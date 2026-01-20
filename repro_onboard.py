import asyncio
import httpx
import json

async def onboard():
    url = "http://localhost:8002/api/v1/organizations/onboard"
    payload = {
        "organization_name": "Test Org 2",
        "owner_email": "testowner2@example.com",
        "owner_password": "Password123!",
        "owner_first_name": "Test",
        "owner_last_name": "Owner",
        "plan": "free"
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
    asyncio.run(onboard())
