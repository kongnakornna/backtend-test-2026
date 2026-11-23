from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.unit_of_work import UnitOfWork
from src.core.exceptions import ConflictError
from src.infrastructure.repositories.classroom_repository import SqlAlchemyClassroomRepository
from src.infrastructure.repositories.school_repository import SqlAlchemySchoolRepository
from src.infrastructure.repositories.student_repository import SqlAlchemyStudentRepository
from src.infrastructure.repositories.teacher_repository import SqlAlchemyTeacherRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schools = SqlAlchemySchoolRepository(session)
        self.classrooms = SqlAlchemyClassroomRepository(session)
        self.teachers = SqlAlchemyTeacherRepository(session)
        self.students = SqlAlchemyStudentRepository(session)

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("The data conflicts with an existing record") from exc

    async def rollback(self) -> None:
        await self.session.rollback()
