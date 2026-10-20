from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, ForeignKey, DateTime, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    subjects: Mapped[list["Subject"]] = relationship(back_populates="domain", cascade="all, delete-orphan")
    concepts: Mapped[list["Concept"]] = relationship(back_populates="domain", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    domain: Mapped["Domain"] = relationship(back_populates="subjects")
    concepts: Mapped[list["Concept"]] = relationship(back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("domain_id", "name", name="uq_subject_domain_name"),
        Index("ix_subject_domain_id", "domain_id"),
    )


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    evidence_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assessment_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    domain: Mapped["Domain"] = relationship(back_populates="concepts")
    subject: Mapped["Subject"] = relationship(back_populates="concepts")
    prerequisites: Mapped[list["ConceptPrerequisite"]] = relationship(
        foreign_keys="ConceptPrerequisite.concept_id",
        back_populates="concept",
        cascade="all, delete-orphan",
    )
    dependents: Mapped[list["ConceptPrerequisite"]] = relationship(
        foreign_keys="ConceptPrerequisite.prerequisite_id",
        back_populates="prerequisite",
        cascade="all, delete-orphan",
    )
    progress_records: Mapped[list["ConceptProgress"]] = relationship(back_populates="concept", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("domain_id", "concept_id", name="uq_concept_domain_concept_id"),
        Index("ix_concept_domain_id", "domain_id"),
        Index("ix_concept_subject_id", "subject_id"),
    )


class ConceptPrerequisite(Base):
    __tablename__ = "concept_prerequisites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    weight: Mapped[float] = mapped_column(default=1.0, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    concept: Mapped["Concept"] = relationship(foreign_keys=[concept_id], back_populates="prerequisites")
    prerequisite: Mapped["Concept"] = relationship(foreign_keys=[prerequisite_id], back_populates="dependents")

    __table_args__ = (
        UniqueConstraint("concept_id", "prerequisite_id", name="uq_concept_prerequisite"),
        Index("ix_concept_prereq_concept", "concept_id"),
        Index("ix_concept_prereq_prereq", "prerequisite_id"),
    )


class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    progress_records: Mapped[list["ConceptProgress"]] = relationship(back_populates="child_profile", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_child_profile_user_id", "user_id"),
    )


class ConceptProgress(Base):
    __tablename__ = "concept_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    child_profile_id: Mapped[int] = mapped_column(ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")  # not_started, learning, known, assessed
    evidence_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    child_profile: Mapped["ChildProfile"] = relationship(back_populates="progress_records")
    concept: Mapped["Concept"] = relationship(back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint("child_profile_id", "concept_id", name="uq_progress_child_concept"),
        Index("ix_progress_child_profile", "child_profile_id"),
        Index("ix_progress_concept", "concept_id"),
        Index("ix_progress_state", "state"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_resource", "resource_type", "resource_id"),
        Index("ix_audit_log_created_at", "created_at"),
    )