from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import json

from app.core.database import get_db
from app.models import Domain, Subject, Concept, ConceptPrerequisite

router = APIRouter()


class ImportResult(BaseModel):
    domains_created: int
    subjects_created: int
    concepts_created: int
    prerequisites_created: int
    errors: list[str]


@router.post("/import/taxonomy", response_model=ImportResult)
async def import_taxonomy(
    file: UploadFile = File(...),
    domain_name: str = "default",
    domain_display_name: str = "Default Domain",
    db: AsyncSession = Depends(get_db),
):
    """Import taxonomy from JSONL file."""
    content = await file.read()
    lines = content.decode("utf-8").strip().split("\n")

    errors = []
    domains_created = 0
    subjects_created = 0
    concepts_created = 0
    prerequisites_created = 0

    # Get or create domain
    result = await db.execute(select(Domain).where(Domain.name == domain_name))
    domain = result.scalar_one_or_none()
    if not domain:
        domain = Domain(name=domain_name, display_name=domain_display_name, is_default=True)
        db.add(domain)
        await db.flush()
        domains_created = 1

    subject_cache = {}
    concept_cache = {}

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            record_type = record.get("type")

            if record_type == "subject":
                subject_name = record.get("name")
                if not subject_name:
                    errors.append(f"Line {line_num}: subject missing name")
                    continue

                if subject_name not in subject_cache:
                    subject = Subject(
                        domain_id=domain.id,
                        name=subject_name,
                        display_name=record.get("display_name", subject_name),
                        description=record.get("description"),
                        age_min=record.get("age_min"),
                        age_max=record.get("age_max"),
                        difficulty_min=record.get("difficulty_min"),
                        difficulty_max=record.get("difficulty_max"),
                        sort_order=record.get("sort_order", 0),
                        metadata_=record.get("metadata", {}),
                    )
                    db.add(subject)
                    await db.flush()
                    subject_cache[subject_name] = subject
                    subjects_created += 1

            elif record_type == "concept":
                concept_id = record.get("concept_id")
                subject_name = record.get("subject")
                if not concept_id or not subject_name:
                    errors.append(f"Line {line_num}: concept missing concept_id or subject")
                    continue

                subject = subject_cache.get(subject_name)
                if not subject:
                    errors.append(f"Line {line_num}: subject '{subject_name}' not found")
                    continue

                concept = Concept(
                    domain_id=domain.id,
                    subject_id=subject.id,
                    concept_id=concept_id,
                    name=record.get("name", concept_id),
                    description=record.get("description"),
                    age_min=record.get("age_min"),
                    age_max=record.get("age_max"),
                    difficulty=record.get("difficulty"),
                    evidence_criteria=record.get("evidence_criteria"),
                    assessment_prompt=record.get("assessment_prompt"),
                    metadata_=record.get("metadata", {}),
                )
                db.add(concept)
                await db.flush()
                concept_cache[concept_id] = concept
                concepts_created += 1

            elif record_type == "prerequisite":
                concept_id = record.get("concept_id")
                prereq_id = record.get("prerequisite_id")
                if not concept_id or not prereq_id:
                    errors.append(f"Line {line_num}: prerequisite missing concept_id or prerequisite_id")
                    continue

                concept = concept_cache.get(concept_id)
                prereq = concept_cache.get(prereq_id)
                if not concept or not prereq:
                    errors.append(f"Line {line_num}: concept or prerequisite not found in import")
                    continue

                prereq_rel = ConceptPrerequisite(
                    concept_id=concept.id,
                    prerequisite_id=prereq.id,
                    weight=record.get("weight", 1.0),
                    metadata_=record.get("metadata", {}),
                )
                db.add(prereq_rel)
                prerequisites_created += 1

        except json.JSONDecodeError as e:
            errors.append(f"Line {line_num}: invalid JSON - {str(e)}")
        except Exception as e:
            errors.append(f"Line {line_num}: {str(e)}")

    await db.commit()

    return ImportResult(
        domains_created=domains_created,
        subjects_created=subjects_created,
        concepts_created=concepts_created,
        prerequisites_created=prerequisites_created,
        errors=errors,
    )