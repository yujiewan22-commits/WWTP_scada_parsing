from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(100))
    org_type: Mapped[str | None] = mapped_column(String(50))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
