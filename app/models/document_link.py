from sqlalchemy import String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class DocumentStructureLink(Base, TimestampMixin):
    __tablename__ = "document_structure_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)

    # process_system / facility / facility_unit
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    confidence: Mapped[float | None] = mapped_column(Float)
    match_status: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    evidence_text: Mapped[str | None] = mapped_column(Text)
    source_region: Mapped[str | None] = mapped_column(String(200))
