import pytest
from httpx import AsyncClient, ASGITransport
import io
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Base


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


@pytest.mark.asyncio
async def test_import_taxonomy(client):
    jsonl_content = """{"type": "subject", "name": "math", "display_name": "Mathematics", "age_min": 5, "age_max": 10}
{"type": "concept", "concept_id": "counting", "subject": "math", "name": "Counting to 10", "difficulty": 1}
{"type": "concept", "concept_id": "addition", "subject": "math", "name": "Basic Addition", "difficulty": 2}
{"type": "prerequisite", "concept_id": "addition", "prerequisite_id": "counting", "weight": 1.0}"""

    file = io.BytesIO(jsonl_content.encode("utf-8"))
    response = await client.post(
        "/api/v1/import/taxonomy",
        files={"file": ("taxonomy.jsonl", file, "application/json")},
        data={"domain_name": "test-import", "domain_display_name": "Test Import"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["domains_created"] == 1
    assert data["subjects_created"] == 1
    assert data["concepts_created"] == 2
    assert data["prerequisites_created"] == 1
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_import_taxonomy_missing_subject(client):
    jsonl_content = """{"type": "concept", "concept_id": "counting", "subject": "math", "name": "Counting to 10"}"""

    file = io.BytesIO(jsonl_content.encode("utf-8"))
    response = await client.post(
        "/api/v1/import/taxonomy",
        files={"file": ("taxonomy.jsonl", file, "application/json")},
        data={"domain_name": "test-import-2", "domain_display_name": "Test Import 2"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["errors"]
    assert any("subject 'math' not found" in e for e in data["errors"])