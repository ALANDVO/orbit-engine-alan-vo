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
    concept3 = Concept(
        domain_id=domain.id,
        subject_id=subject.id,
        concept_id="subtraction",
        name="Basic Subtraction",
        difficulty=2,
    )
    db_session.add_all([concept1, concept2, concept3])
    await db_session.flush()
    return domain, subject, concept1, concept2, concept3


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
async def test_filter_by_age_range(client, setup_domain):
    domain, subject, c1, c2, c3 = setup_domain

    # Update concepts with age ranges
    c1.age_min = 5
    c1.age_max = 7
    c2.age_min = 7
    c2.age_max = 9
    c3.age_min = 8
    c3.age_max = 10
    await db_session.commit()

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&age_min=6&age_max=8")
    assert response.status_code == 200
    data = response.json()
    # Should include concepts with age range overlapping 6-8
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_filter_by_difficulty(client, setup_domain):
    domain, subject, c1, c2, c3 = setup_domain

    response = await client.get(f"/api/v1/concepts?domain_id={domain.id}&difficulty_min=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for c in data["concepts"]:
        assert c["difficulty"] >= 2