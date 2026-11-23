from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base
from src.infrastructure.models.classroom import ClassroomModel

teacher_classrooms = Table(
    "teacher_classrooms",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "classroom_id",
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class TeacherModel(Base):
    __tablename__ = "teachers"
    __table_args__ = (CheckConstraint("gender IN ('M', 'F', 'O')", name="gender_valid"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))

    # selectin: one extra query per batch of teachers (no N+1, safe under asyncio)
    classrooms: Mapped[list[ClassroomModel]] = relationship(
        secondary=teacher_classrooms,
        lazy="selectin",
        order_by=ClassroomModel.id,
        passive_deletes=True,
    )
