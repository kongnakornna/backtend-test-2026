from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.session import Base


teacher_classroom = Table(
    "teacher_classroom",
    Base.metadata,
    Column(
        "teacher_id",
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "classroom_id",
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class SchoolModel(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    abbreviation: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(Text)

    # Deleting a school removes its classrooms, teachers and (via classrooms) students.
    classrooms = relationship(
        "ClassroomModel",
        back_populates="school",
        cascade="all, delete-orphan",
    )
    teachers = relationship(
        "TeacherModel",
        back_populates="school",
        cascade="all, delete-orphan",
    )


class ClassroomModel(Base):
    __tablename__ = "classrooms"
    __table_args__ = (UniqueConstraint("school_id", "year_level", "section"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE")
    )
    year_level: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(50))

    school = relationship("SchoolModel", back_populates="classrooms")
    students = relationship(
        "StudentModel",
        back_populates="classroom",
        cascade="all, delete-orphan",
    )
    teachers = relationship(
        "TeacherModel",
        secondary=teacher_classroom,
        back_populates="classrooms",
    )


class TeacherModel(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE")
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))

    school = relationship("SchoolModel", back_populates="teachers")
    classrooms = relationship(
        "ClassroomModel",
        secondary=teacher_classroom,
        back_populates="teachers",
    )


class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="CASCADE")
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))

    classroom = relationship("ClassroomModel", back_populates="students")
