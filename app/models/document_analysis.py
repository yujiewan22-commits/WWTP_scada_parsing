from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class DocumentAnalysis(Base, TimestampMixin):
    __tablename__ = "document_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    analysis_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(120))
    document_type: Mapped[str | None] = mapped_column(String(80))
    title: Mapped[str | None] = mapped_column(String(300))
    drawing_no: Mapped[str | None] = mapped_column(String(120))
    discipline: Mapped[str | None] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)
    raw_result_json: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
