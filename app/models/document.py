from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    document_type: Mapped[str | None] = mapped_column(String(80), index=True)
    title: Mapped[str | None] = mapped_column(String(300))
    drawing_no: Mapped[str | None] = mapped_column(String(120), index=True)
    revision: Mapped[str | None] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)
    discipline: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text)

    ai_status: Mapped[str] = mapped_column(String(30), default="UNANALYZED", nullable=False)
