from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class StudentModel(Base):
    __tablename__ = "students"
    __table_args__ = (CheckConstraint("gender IN ('M', 'F', 'O')", name="gender_valid"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="CASCADE"), index=True
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))
