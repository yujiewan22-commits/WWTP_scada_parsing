from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


# ============================================================
# Organization
# ============================================================

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


# ============================================================
# Plant
# ============================================================

class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    phase: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship()


# ============================================================
# SCADA Document
# ============================================================

class ScadaDocument(Base):
    __tablename__ = "scada_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ai_status: Mapped[str] = mapped_column(
        String(50),
        default="UNANALYZED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    plant: Mapped["Plant"] = relationship()


# ============================================================
# Agent 1 Result
# ============================================================

class ScadaFacilityAnalysis(Base):
    __tablename__ = "scada_facility_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("scada_documents.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
    )

    provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    result_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# Agent 2 Result
# ============================================================

class ScadaFacilityUnitAnalysis(Base):
    __tablename__ = "scada_facility_unit_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("scada_documents.id"),
        nullable=False,
        index=True,
    )

    facility_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    facility_standard_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
    )

    provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    result_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )