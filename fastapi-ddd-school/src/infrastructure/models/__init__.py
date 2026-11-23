"""Import every model so Base.metadata is complete (used by Alembic and tests)."""

from src.infrastructure.models.classroom import ClassroomModel
from src.infrastructure.models.school import SchoolModel
from src.infrastructure.models.student import StudentModel
from src.infrastructure.models.teacher import TeacherModel, teacher_classrooms

__all__ = ["ClassroomModel", "SchoolModel", "StudentModel", "TeacherModel", "teacher_classrooms"]
