from abc import ABC, abstractmethod

from src.domain.repositories.classroom_repository import ClassroomRepository
from src.domain.repositories.school_repository import SchoolRepository
from src.domain.repositories.student_repository import StudentRepository
from src.domain.repositories.teacher_repository import TeacherRepository


class UnitOfWork(ABC):
    """Groups the repositories of one business transaction."""

    schools: SchoolRepository
    classrooms: ClassroomRepository
    teachers: TeacherRepository
    students: StudentRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
