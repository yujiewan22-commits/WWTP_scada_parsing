from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class Plant(Base, TimestampMixin):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))

    # 业务正式名称，例如：肇东1期
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # 期数仅作为描述字段，例如：1期
    phase: Mapped[str | None] = mapped_column(String(50), index=True)

    code: Mapped[str | None] = mapped_column(String(80), unique=True)
    location: Mapped[str | None] = mapped_column(String(300))
    design_capacity: Mapped[float | None] = mapped_column(Float)
    capacity_unit: Mapped[str | None] = mapped_column(String(30), default="m3/d")
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
