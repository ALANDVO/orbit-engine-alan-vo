import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Base
from app.api.auth import TokenData




@pytest.mark.asyncio
async def test_auth_me_requires_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_login_demo_mode(client):
    # With DEMO_MODE=true, login should return demo URL
    response = await client.get("/api/v1/auth/login")
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "/demo-login"