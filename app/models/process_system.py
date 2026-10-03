from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class ProcessSystem(Base, TimestampMixin):
    __tablename__ = "process_systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    system_type: Mapped[str | None] = mapped_column(String(100), index=True)
    aliases: Mapped[str | None] = mapped_column(String(800))
    status: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    source: Mapped[str] = mapped_column(String(30), default="AI", nullable=False)
