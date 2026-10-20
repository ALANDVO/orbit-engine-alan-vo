import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Subject, Concept, Base
from sqlalchemy import select


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def setup_domain(db_session):
    domain = Domain(name="test", display_name="Test Domain", is_default=True)
    db_session.add(domain)
    await db_session.flush()
    subject = Subject(
        domain_id=domain.id,
        name="math",
        display_name="Mathematics",
        age_min=5,
        age_max=10,
    )
    db_session.add(subject)
    await db_session.flush()
    concept1 = Concept(
        domain_id=domain.id,
        subject_id=subject.id,
        concept_id="counting",
        name="Counting to 10",
        difficulty=1,
    )
    concept2 = Concept(
        domain_id=domain.id,
        subject_id=subject.id,
        concept_id="addition",
        name="Basic Addition",
        difficulty=2,
    )
    db_session.add_all([concept1, concept2])
    await db_session.flush()
    return domain, subject, concept1, concept2


@pytest.mark.asyncio
async def test_search_concepts(client, setup_domain):
    domain, subject, concept1, concept2 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["concepts"]) == 2


@pytest.mark.asyncio
async def test_search_concepts_with_query(client, setup_domain):
    domain, subject, concept1, concept2 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&q=counting")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["concepts"][0]["concept_id"] == "counting"


@pytest.mark.asyncio
async def test_search_concepts_by_subject(client, setup_domain):
    domain, subject, concept1, concept2 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&subject_id={subject.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_concept_detail(client, setup_domain):
    domain, subject, concept1, concept2 = setup_domain

    response = await client.get(f"/api/v1/concepts/{concept1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == concept1.id
    assert data["concept_id"] == "counting"
    assert "prerequisites" in data
    assert "dependents" in data


@pytest.mark.asyncio
async def test_concept_graph(client, setup_domain):
    domain, subject, concept1, concept2 = setup_domain

    response = await client.get(f"/api/v1/concepts/{concept1.id}/graph?depth=1")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 1
    assert any(n["id"] == concept1.id for n in data["nodes"])