from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models import Domain, Subject, Concept

router = APIRouter()


class DomainCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    is_default: bool = False
    metadata_: dict = {}


class DomainResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    version: str
    is_default: bool
    metadata_: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DomainListResponse(BaseModel):
    domains: list[DomainResponse]
    total: int


@router.get("/domains", response_model=DomainListResponse)
async def list_domains(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await db.execute(
        select(Domain).order_by(Domain.name).limit(limit).offset(offset)
    )
    domains = result.scalars().all()

    total_result = await db.execute(select(func.count(Domain.id)))
    total = total_result.scalar() or 0

    return DomainListResponse(
        domains=[DomainResponse.model_validate(d) for d in domains],
        total=total,
    )


@router.get("/domains/{domain_id}", response_model=DomainResponse)
async def get_domain(domain_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainResponse.model_validate(domain)


@router.post("/domains", response_model=DomainResponse, status_code=201)
async def create_domain(domain: DomainCreate, db: AsyncSession = Depends(get_db)):
    db_domain = Domain(**domain.model_dump())
    db.add(db_domain)
    await db.commit()
    await db.refresh(db_domain)
    return DomainResponse.model_validate(db_domain)