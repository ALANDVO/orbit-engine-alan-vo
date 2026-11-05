import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from app.main import app
from app.core.database import get_db, async_session_maker, engine
from app.models import Domain, Subject, Concept, ChildProfile, ConceptProgress, Base
from sqlalchemy import select






@pytest.mark.asyncio
async def test_create_profile(client, setup_data):
    domain, subject, concept = setup_data

    response = await client.post(
        "/api/v1/profiles?user_id=test-user",
        json={"name": "Test Child", "birth_date": "2018-01-15T00:00:00Z"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Child"
    assert data["user_id"] == "test-user"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_profiles(client, setup_data):
    domain, subject, concept = setup_data

    # Create a profile first
    await client.post(
        "/api/v1/profiles?user_id=test-user",
        json={"name": "Test Child"},
    )

    response = await client.get("/api/v1/profiles?user_id=test-user")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["profiles"]) == 1


@pytest.mark.asyncio
async def test_upsert_progress(client, setup_data):
    domain, subject, concept = setup_data

    # Create profile
    profile_resp = await client.post(
        "/api/v1/profiles?user_id=test-user",
        json={"name": "Test Child"},
    )
    profile_id = profile_resp.json()["id"]

    # Upsert progress
    response = await client.post(
        f"/api/v1/profiles/{profile_id}/progress",
        json={"concept_id": concept.id, "state": "learning", "evidence_notes": "Started practicing"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["concept_id"] == concept.id
    assert data["state"] == "learning"
    assert data["evidence_notes"] == "Started practicing"


@pytest.mark.asyncio
async def test_upsert_progress_updates_existing(client, setup_data):
    domain, subject, concept = setup_data

    profile_resp = await client.post(
        "/api/v1/profiles?user_id=test-user",
        json={"name": "Test Child"},
    )
    profile_id = profile_resp.json()["id"]

    # First upsert
    await client.post(
        f"/api/v1/profiles/{profile_id}/progress",
        json={"concept_id": concept.id, "state": "learning"},
    )

    # Second upsert - should update
    response = await client.post(
        f"/api/v1/profiles/{profile_id}/progress",
        json={"concept_id": concept.id, "state": "known", "evidence_notes": "Mastered"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["state"] == "known"
    assert data["evidence_notes"] == "Mastered"
    assert data["assessed_at"] is None  # not assessed state


@pytest.mark.asyncio
async def test_get_progress(client, setup_data):
    domain, subject, concept = setup_data

    profile_resp = await client.post(
        "/api/v1/profiles?user_id=test-user",
        json={"name": "Test Child"},
    )
    profile_id = profile_resp.json()["id"]

    await client.post(
        f"/api/v1/profiles/{profile_id}/progress",
        json={"concept_id": concept.id, "state": "known"},
    )

    response = await client.get(f"/api/v1/profiles/{profile_id}/progress")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["progress"][0]["state"] == "known"