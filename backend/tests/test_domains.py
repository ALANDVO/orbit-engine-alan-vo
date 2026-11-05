import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Base
from sqlalchemy import select




@pytest.mark.asyncio
async def test_list_domains_empty(client):
    response = await client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert data["domains"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_domain(client):
    response = await client.post(
        "/api/v1/domains",
        json={"name": "test-domain", "display_name": "Test Domain", "description": "A test domain"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-domain"
    assert data["display_name"] == "Test Domain"
    assert data["description"] == "A test domain"
    assert data["is_default"] is False
    assert "id" in data


@pytest.mark.asyncio
async def test_get_domain(client):
    create_resp = await client.post(
        "/api/v1/domains",
        json={"name": "test-domain-2", "display_name": "Test Domain 2"},
    )
    domain_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/domains/{domain_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == domain_id
    assert data["name"] == "test-domain-2"


@pytest.mark.asyncio
async def test_get_domain_not_found(client):
    response = await client.get("/api/v1/domains/999")
    assert response.status_code == 404