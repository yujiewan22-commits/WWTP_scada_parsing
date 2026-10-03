from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class FacilityUnit(Base, TimestampMixin):
    __tablename__ = "facility_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    unit_type: Mapped[str | None] = mapped_column(String(100), index=True)
    sequence_no: Mapped[int | None] = mapped_column(Integer)

    # 如果只识别到“池格×4”，但没有明确编号，可记录数量
    quantity: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    source: Mapped[str] = mapped_column(String(30), default="AI", nullable=False)
