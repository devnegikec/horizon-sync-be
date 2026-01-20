
import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from shared.config import settings

def create_test_app():
    """Create a mock FastAPI app with project CORS settings."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/test-cors")
    async def test_cors():
        return {"message": "CORS works"}

    return app

@pytest.fixture
def client():
    app = create_test_app()
    return TestClient(app)

def test_cors_preflight(client):
    """Test CORS preflight (OPTIONS) request."""
    response = client.options(
        "/test-cors",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]
    assert response.headers["access-control-allow-credentials"] == "true"

def test_cors_get_request(client):
    """Test CORS GET request with Origin header."""
    response = client.get(
        "/test-cors",
        headers={"Origin": "http://example.com"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert response.headers["access-control-allow-credentials"] == "true"

def test_cors_disallowed_origin():
    """
    Test with disallowed origin if CORS_ORIGINS was restricted.
    Since we set it to ['*'], all origins should be allowed.
    """
    app = FastAPI()
    # Mocking restricted settings for comparison if needed, 
    # but here we test our actual settings.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS, # This is ["*"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    client = TestClient(app)
    
    response = client.get(
        "/",
        headers={"Origin": "http://any-origin.com"},
    )
    # CORSMiddleware with ["*"] and allow_credentials=True 
    # actually returns the Origin value in access-control-allow-origin
    assert response.headers["access-control-allow-origin"] == "http://any-origin.com"
