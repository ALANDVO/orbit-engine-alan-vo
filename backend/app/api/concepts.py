from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models import Concept, Subject, ConceptPrerequisite

router = APIRouter()


class ConceptPrerequisiteResponse(BaseModel):
    concept_id: int
    prerequisite_id: int
    weight: float

    class Config:
        from_attributes = True


class ConceptResponse(BaseModel):
    id: int
    domain_id: int
    subject_id: int
    concept_id: str
    name: str
    description: Optional[str]
    age_min: Optional[int]
    age_max: Optional[int]
    difficulty: Optional[int]
    evidence_criteria: Optional[str]
    assessment_prompt: Optional[str]
    metadata_: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ConceptDetailResponse(ConceptResponse):
    prerequisites: list[ConceptPrerequisiteResponse] = []
    dependents: list[ConceptPrerequisiteResponse] = []


class ConceptListResponse(BaseModel):
    concepts: list[ConceptResponse]
    total: int


class ConceptSearchParams(BaseModel):
    q: Optional[str] = None
    domain_id: Optional[int] = None
    subject_id: Optional[int] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    difficulty_min: Optional[int] = None
    difficulty_max: Optional[int] = None
    limit: int = 50
    offset: int = 0


@router.get("/concepts", response_model=ConceptListResponse)
async def search_concepts(
    q: Optional[str] = Query(None),
    domain_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    age_min: Optional[int] = Query(None),
    age_max: Optional[int] = Query(None),
    difficulty_min: Optional[int] = Query(None),
    difficulty_max: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Concept)

    if q:
        stmt = stmt.where(
            or_(
                Concept.name.ilike(f"%{q}%"),
                Concept.concept_id.ilike(f"%{q}%"),
                Concept.description.ilike(f"%{q}%"),
            )
        )
    if domain_id:
        stmt = stmt.where(Concept.domain_id == domain_id)
    if subject_id:
        stmt = stmt.where(Concept.subject_id == subject_id)
    if age_min:
        stmt = stmt.where(Concept.age_min >= age_min)
    if age_max:
        stmt = stmt.where(Concept.age_max <= age_max)
    if difficulty_min:
        stmt = stmt.where(Concept.difficulty >= difficulty_min)
    if difficulty_max:
        stmt = stmt.where(Concept.difficulty <= difficulty_max)

    stmt = stmt.order_by(Concept.name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    concepts = result.scalars().all()

    count_stmt = select(func.count(Concept.id))
    if q:
        count_stmt = count_stmt.where(
            or_(
                Concept.name.ilike(f"%{q}%"),
                Concept.concept_id.ilike(f"%{q}%"),
                Concept.description.ilike(f"%{q}%"),
            )
        )
    if domain_id:
        count_stmt = count_stmt.where(Concept.domain_id == domain_id)
    if subject_id:
        count_stmt = count_stmt.where(Concept.subject_id == subject_id)
    if age_min:
        count_stmt = count_stmt.where(Concept.age_min >= age_min)
    if age_max:
        count_stmt = count_stmt.where(Concept.age_max <= age_max)
    if difficulty_min:
        count_stmt = count_stmt.where(Concept.difficulty >= difficulty_min)
    if difficulty_max:
        count_stmt = count_stmt.where(Concept.difficulty <= difficulty_max)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    return ConceptListResponse(
        concepts=[ConceptResponse.model_validate(c) for c in concepts],
        total=total,
    )


@router.get("/concepts/{concept_id}", response_model=ConceptDetailResponse)
async def get_concept(concept_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Concept)
        .options(selectinload(Concept.prerequisites), selectinload(Concept.dependents))
        .where(Concept.id == concept_id)
    )
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    prereqs = [
        ConceptPrerequisiteResponse(
            concept_id=p.concept_id,
            prerequisite_id=p.prerequisite_id,
            weight=p.weight,
        )
        for p in concept.prerequisites
    ]
    dependents = [
        ConceptPrerequisiteResponse(
            concept_id=d.concept_id,
            prerequisite_id=d.prerequisite_id,
            weight=d.weight,
        )
        for d in concept.dependents
    ]

    return ConceptDetailResponse(
        **ConceptResponse.model_validate(concept).model_dump(),
        prerequisites=prereqs,
        dependents=dependents,
    )


@router.get("/concepts/{concept_id}/graph")
async def get_concept_graph(
    concept_id: int,
    depth: int = Query(2, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    """Get subgraph around a concept for visualization."""
    result = await db.execute(select(Concept).where(Concept.id == concept_id))
    center = result.scalar_one_or_none()
    if not center:
        raise HTTPException(status_code=404, detail="Concept not found")

    # BFS to collect nodes within depth
    visited = {center.id}
    nodes = [center]
    edges = []
    current_level = [center]

    for _ in range(depth):
        next_level = []
        for node in current_level:
            # Prerequisites
            prereq_result = await db.execute(
                select(ConceptPrerequisite, Concept)
                .join(Concept, ConceptPrerequisite.prerequisite_id == Concept.id)
                .where(ConceptPrerequisite.concept_id == node.id)
            )
            for prereq, prereq_concept in prereq_result.all():
                edges.append({
                    "source": prereq_concept.id,
                    "target": node.id,
                    "weight": prereq.weight,
                })
                if prereq_concept.id not in visited:
                    visited.add(prereq_concept.id)
                    nodes.append(prereq_concept)
                    next_level.append(prereq_concept)

            # Dependents
            dep_result = await db.execute(
                select(ConceptPrerequisite, Concept)
                .join(Concept, ConceptPrerequisite.concept_id == Concept.id)
                .where(ConceptPrerequisite.prerequisite_id == node.id)
            )
            for dep, dep_concept in dep_result.all():
                edges.append({
                    "source": node.id,
                    "target": dep_concept.id,
                    "weight": dep.weight,
                })
                if dep_concept.id not in visited:
                    visited.add(dep_concept.id)
                    nodes.append(dep_concept)
                    next_level.append(dep_concept)
        current_level = next_level
        if not current_level:
            break

    return {
        "nodes": [
            {
                "id": n.id,
                "concept_id": n.concept_id,
                "name": n.name,
                "subject_id": n.subject_id,
                "difficulty": n.difficulty,
            }
            for n in nodes
        ],
        "edges": edges,
    }