import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Subject, Concept, Base
from sqlalchemy import select






@pytest.mark.asyncio
async def test_search_concepts(client, setup_domain):
    domain, subject, concept1, concept2, concept3 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["concepts"]) == 3


@pytest.mark.asyncio
async def test_search_concepts_with_query(client, setup_domain):
    domain, subject, concept1, concept2, concept3 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&q=counting")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["concepts"][0]["concept_id"] == "counting"


@pytest.mark.asyncio
async def test_search_concepts_by_subject(client, setup_domain):
    domain, subject, concept1, concept2, concept3 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&subject_id={subject.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_get_concept_detail(client, setup_domain):
    domain, subject, concept1, concept2, concept3 = setup_domain

    response = await client.get(f"/api/v1/concepts/{concept1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == concept1.id
    assert data["concept_id"] == "counting"
    assert "prerequisites" in data
    assert "dependents" in data


@pytest.mark.asyncio
async def test_concept_graph(client, setup_domain):
    domain, subject, concept1, concept2, concept3 = setup_domain

    response = await client.get(f"/api/v1/concepts/{concept1.id}/graph?depth=1")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 1
    assert any(n["id"] == concept1.id for n in data["nodes"])