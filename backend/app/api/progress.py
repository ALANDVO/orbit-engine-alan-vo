from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models import ChildProfile, ConceptProgress, Concept

router = APIRouter()


class ChildProfileCreate(BaseModel):
    name: str
    birth_date: Optional[str] = None
    metadata_: dict = {}


class ChildProfileResponse(BaseModel):
    id: int
    user_id: str
    name: str
    birth_date: Optional[str]
    metadata_: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ChildProfileListResponse(BaseModel):
    profiles: list[ChildProfileResponse]
    total: int


class ConceptProgressCreate(BaseModel):
    concept_id: int
    state: str  # not_started, learning, known, assessed
    evidence_notes: Optional[str] = None


class ConceptProgressResponse(BaseModel):
    id: int
    child_profile_id: int
    concept_id: int
    state: str
    evidence_notes: Optional[str]
    assessed_at: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProgressListResponse(BaseModel):
    progress: list[ConceptProgressResponse]
    total: int


@router.get("/profiles", response_model=ChildProfileListResponse)
async def list_profiles(
    user_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ChildProfile).where(ChildProfile.user_id == user_id).order_by(ChildProfile.name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    profiles = result.scalars().all()

    count_stmt = select(func.count(ChildProfile.id)).where(ChildProfile.user_id == user_id)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    return ChildProfileListResponse(
        profiles=[ChildProfileResponse.model_validate(p) for p in profiles],
        total=total,
    )


@router.get("/profiles/{profile_id}", response_model=ChildProfileResponse)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChildProfile).where(ChildProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ChildProfileResponse.model_validate(profile)


@router.post("/profiles", response_model=ChildProfileResponse, status_code=201)
async def create_profile(
    profile: ChildProfileCreate,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    birth_date = None
    if profile.birth_date:
        birth_date = datetime.fromisoformat(profile.birth_date.replace("Z", "+00:00"))

    db_profile = ChildProfile(
        user_id=user_id,
        name=profile.name,
        birth_date=birth_date,
        metadata_=profile.metadata_,
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return ChildProfileResponse.model_validate(db_profile)


@router.patch("/profiles/{profile_id}", response_model=ChildProfileResponse)
async def update_profile(
    profile_id: int,
    name: Optional[str] = None,
    birth_date: Optional[str] = None,
    metadata_: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ChildProfile).where(ChildProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if name is not None:
        profile.name = name
    if birth_date is not None:
        profile.birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00"))
    if metadata_ is not None:
        profile.metadata_ = metadata_

    await db.commit()
    await db.refresh(profile)
    return ChildProfileResponse.model_validate(profile)


@router.delete("/profiles/{profile_id}", status_code=204)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChildProfile).where(ChildProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)
    await db.commit()


@router.get("/profiles/{profile_id}/progress", response_model=ProgressListResponse)
async def get_progress(
    profile_id: int,
    state: Optional[str] = Query(None),
    domain_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ChildProfile).where(ChildProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    stmt = (
        select(ConceptProgress)
        .join(Concept)
        .where(ConceptProgress.child_profile_id == profile_id)
    )

    if state:
        stmt = stmt.where(ConceptProgress.state == state)
    if domain_id:
        stmt = stmt.where(Concept.domain_id == domain_id)
    if subject_id:
        stmt = stmt.where(Concept.subject_id == subject_id)

    stmt = stmt.order_by(ConceptProgress.updated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    progress = result.scalars().all()

    count_stmt = select(func.count(ConceptProgress.id)).where(ConceptProgress.child_profile_id == profile_id)
    if state:
        count_stmt = count_stmt.where(ConceptProgress.state == state)
    if domain_id:
        count_stmt = count_stmt.join(Concept).where(Concept.domain_id == domain_id)
    if subject_id:
        count_stmt = count_stmt.join(Concept).where(Concept.subject_id == subject_id)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    return ProgressListResponse(
        progress=[ConceptProgressResponse.model_validate(p) for p in progress],
        total=total,
    )


@router.post("/profiles/{profile_id}/progress", response_model=ConceptProgressResponse, status_code=201)
async def upsert_progress(
    profile_id: int,
    progress: ConceptProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ChildProfile).where(ChildProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await db.execute(select(Concept).where(Concept.id == progress.concept_id))
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Upsert
    existing = await db.execute(
        select(ConceptProgress).where(
            ConceptProgress.child_profile_id == profile_id,
            ConceptProgress.concept_id == progress.concept_id,
        )
    )
    existing_progress = existing.scalar_one_or_none()

    if existing_progress:
        existing_progress.state = progress.state
        existing_progress.evidence_notes = progress.evidence_notes
        if progress.state == "assessed":
            existing_progress.assessed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_progress)
        return ConceptProgressResponse.model_validate(existing_progress)
    else:
        new_progress = ConceptProgress(
            child_profile_id=profile_id,
            concept_id=progress.concept_id,
            state=progress.state,
            evidence_notes=progress.evidence_notes,
            assessed_at=datetime.now(timezone.utc) if progress.state == "assessed" else None,
        )
        db.add(new_progress)
        await db.commit()
        await db.refresh(new_progress)
        return ConceptProgressResponse.model_validate(new_progress)