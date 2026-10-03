from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    project_type_id: Mapped[int] = mapped_column(ForeignKey("project_types.id"), nullable=False)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    lead_organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="in_progress", nullable=False)
