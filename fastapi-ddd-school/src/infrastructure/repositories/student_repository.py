from sqlalchemy import delete, select

from src.core.exceptions import NotFoundError
from src.domain.entities.student import Student
from src.domain.repositories.criteria import PersonCriteria
from src.domain.repositories.student_repository import StudentRepository
from src.infrastructure.models import ClassroomModel, StudentModel
from src.infrastructure.repositories.base import SqlAlchemyRepository
from src.infrastructure.repositories.person_filters import apply_name_gender_filters


def _to_entity(model: StudentModel) -> Student:
    return Student(
        id=model.id,
        classroom_id=model.classroom_id,
        first_name=model.first_name,
        last_name=model.last_name,
        gender=model.gender,
    )


class SqlAlchemyStudentRepository(SqlAlchemyRepository, StudentRepository):
    async def get(self, student_id: int) -> Student | None:
        model = await self.session.get(StudentModel, student_id)
        return _to_entity(model) if model else None

    async def save(self, student: Student) -> Student:
        if student.id is None:
            model = StudentModel()
            self.session.add(model)
        else:
            model = await self.session.get(StudentModel, student.id)
            if model is None:
                raise NotFoundError(f"Student {student.id} not found")
        model.classroom_id = student.classroom_id
        model.first_name = student.first_name
        model.last_name = student.last_name
        model.gender = student.gender.value
        await self._flush()
        return _to_entity(model)

    async def delete(self, student_id: int) -> None:
        await self.session.execute(delete(StudentModel).where(StudentModel.id == student_id))

    async def search(
        self, criteria: PersonCriteria, *, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Student], int]:
        stmt = select(StudentModel).order_by(StudentModel.id)
        if criteria.school_id is not None:
            stmt = stmt.where(
                StudentModel.classroom_id.in_(
                    select(ClassroomModel.id).where(ClassroomModel.school_id == criteria.school_id)
                )
            )
        if criteria.classroom_id is not None:
            stmt = stmt.where(StudentModel.classroom_id == criteria.classroom_id)
        stmt = apply_name_gender_filters(stmt, StudentModel, criteria)
        rows, total = await self._paginate(stmt, offset, limit)
        return [_to_entity(m) for m in rows], total
