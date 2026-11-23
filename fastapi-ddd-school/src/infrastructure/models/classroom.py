from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ClassroomModel(Base):
    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("school_id", "year_level", "section"),
        CheckConstraint("year_level >= 1", name="year_level_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True
    )
    year_level: Mapped[int]
    section: Mapped[str] = mapped_column(String(20))
