from sqlalchemy import String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class StructureCandidate(Base, TimestampMixin):
    __tablename__ = "structure_candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_name: Mapped[str | None] = mapped_column(String(200), index=True)
    entity_subtype: Mapped[str | None] = mapped_column(String(100))
    quantity: Mapped[int | None] = mapped_column(Integer)
    parent_candidate_id: Mapped[int | None] = mapped_column(Integer, index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    merge_key: Mapped[str | None] = mapped_column(String(300), index=True)
    source_summary: Mapped[str | None] = mapped_column(Text)
