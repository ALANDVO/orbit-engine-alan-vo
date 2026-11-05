import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Subject, Concept, Base
from sqlalchemy import select






@pytest.mark.asyncio
async def test_pagination(client, setup_domain):
    domain, subject, c1, c2, c3 = setup_domain

    # Test limit
    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["concepts"]) == 2
    assert data["total"] == 3

    # Test offset
    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["concepts"]) == 1


@pytest.mark.asyncio
async def test_filter_by_age_range(client, setup_domain, db_session):
    domain, subject, c1, c2, c3 = setup_domain

    # Update concepts with age ranges
    c1.age_min = 5
    c1.age_max = 7
    c2.age_min = 6
    c2.age_max = 8
    c3.age_min = 9
    c3.age_max = 10
    await db_session.commit()

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&age_min=6&age_max=8")
    assert response.status_code == 200
    data = response.json()
    # Should include concepts with age_min >= 6 and age_max <= 8 (c2 only)
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_filter_by_difficulty(client, setup_domain):
    domain, subject, c1, c2, c3 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&difficulty_min=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for c in data["concepts"]:
        assert c["difficulty"] >= 2