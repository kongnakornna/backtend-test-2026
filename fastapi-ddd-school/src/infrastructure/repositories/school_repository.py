from sqlalchemy import delete, func, select

from src.core.exceptions import NotFoundError
from src.domain.entities.school import School, SchoolStats
from src.domain.repositories.school_repository import SchoolRepository
from src.infrastructure.models import ClassroomModel, SchoolModel, StudentModel, TeacherModel
from src.infrastructure.repositories.base import SqlAlchemyRepository


def _to_entity(model: SchoolModel) -> School:
    return School(
        id=model.id, name=model.name, abbreviation=model.abbreviation, address=model.address
    )


class SqlAlchemySchoolRepository(SqlAlchemyRepository, SchoolRepository):
    async def get(self, school_id: int) -> School | None:
        model = await self.session.get(SchoolModel, school_id)
        return _to_entity(model) if model else None

    async def save(self, school: School) -> School:
        if school.id is None:
            model = SchoolModel()
            self.session.add(model)
        else:
            model = await self.session.get(SchoolModel, school.id)
            if model is None:
                raise NotFoundError(f"School {school.id} not found")
        model.name = school.name
        model.abbreviation = school.abbreviation
        model.address = school.address
        await self._flush()
        return _to_entity(model)

    async def delete(self, school_id: int) -> None:
        await self.session.execute(delete(SchoolModel).where(SchoolModel.id == school_id))

    async def search(
        self, *, name: str | None = None, offset: int = 0, limit: int | None = None
    ) -> tuple[list[School], int]:
        stmt = select(SchoolModel).order_by(SchoolModel.id)
        if name:
            stmt = stmt.where(SchoolModel.name.icontains(name, autoescape=True))
        rows, total = await self._paginate(stmt, offset, limit)
        return [_to_entity(m) for m in rows], total

    async def get_stats(self, school_id: int) -> SchoolStats:
        # One round trip with three scalar subqueries; avoids the row explosion
        # of JOINing classrooms x teachers x students.
        classrooms = (
            select(func.count(ClassroomModel.id))
            .where(ClassroomModel.school_id == school_id)
            .scalar_subquery()
        )
        teachers = (
            select(func.count(TeacherModel.id))
            .where(TeacherModel.school_id == school_id)
            .scalar_subquery()
        )
        students = (
            select(func.count(StudentModel.id))
            .join(ClassroomModel, StudentModel.classroom_id == ClassroomModel.id)
            .where(ClassroomModel.school_id == school_id)
            .scalar_subquery()
        )
        row = (await self.session.execute(select(classrooms, teachers, students))).one()
        return SchoolStats(classroom_count=row[0], teacher_count=row[1], student_count=row[2])
