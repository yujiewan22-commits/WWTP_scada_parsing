from sqlalchemy import String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class CandidateEvidence(Base, TimestampMixin):
    __tablename__ = "candidate_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("structure_candidates.id"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence_text: Mapped[str | None] = mapped_column(Text)
    source_region: Mapped[str | None] = mapped_column(String(200))
    source_page: Mapped[int | None] = mapped_column(Integer)
