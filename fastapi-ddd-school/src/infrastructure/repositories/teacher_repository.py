from sqlalchemy import delete, select

from src.core.exceptions import NotFoundError
from src.domain.entities.teacher import Teacher
from src.domain.repositories.criteria import PersonCriteria
from src.domain.repositories.teacher_repository import TeacherRepository
from src.infrastructure.models import ClassroomModel, TeacherModel, teacher_classrooms
from src.infrastructure.repositories.base import SqlAlchemyRepository
from src.infrastructure.repositories.person_filters import apply_name_gender_filters


def _to_entity(model: TeacherModel) -> Teacher:
    return Teacher(
        id=model.id,
        school_id=model.school_id,
        first_name=model.first_name,
        last_name=model.last_name,
        gender=model.gender,
        classroom_ids=[c.id for c in model.classrooms],
    )


class SqlAlchemyTeacherRepository(SqlAlchemyRepository, TeacherRepository):
    async def get(self, teacher_id: int) -> Teacher | None:
        model = await self.session.get(TeacherModel, teacher_id)
        return _to_entity(model) if model else None

    async def save(self, teacher: Teacher) -> Teacher:
        # Query everything before touching the model: a SELECT autoflushes pending
        # objects, and assigning an unloaded collection afterwards would lazy-load
        # (not allowed under asyncio).
        classrooms = (
            list(
                await self.session.scalars(
                    select(ClassroomModel)
                    .where(ClassroomModel.id.in_(teacher.classroom_ids))
                    .order_by(ClassroomModel.id)
                )
            )
            if teacher.classroom_ids
            else []
        )
        if teacher.id is None:
            model = TeacherModel(classrooms=classrooms)
            self.session.add(model)
        else:
            model = await self.session.get(TeacherModel, teacher.id)  # classrooms loaded (selectin)
            if model is None:
                raise NotFoundError(f"Teacher {teacher.id} not found")
            model.classrooms = classrooms
        model.school_id = teacher.school_id
        model.first_name = teacher.first_name
        model.last_name = teacher.last_name
        model.gender = teacher.gender.value
        await self._flush()
        return _to_entity(model)

    async def delete(self, teacher_id: int) -> None:
        await self.session.execute(delete(TeacherModel).where(TeacherModel.id == teacher_id))

    async def search(
        self, criteria: PersonCriteria, *, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Teacher], int]:
        stmt = select(TeacherModel).order_by(TeacherModel.id)
        if criteria.school_id is not None:
            stmt = stmt.where(TeacherModel.school_id == criteria.school_id)
        if criteria.classroom_id is not None:
            # EXISTS on the association table: no JOIN duplicates, no DISTINCT needed
            stmt = stmt.where(TeacherModel.classrooms.any(ClassroomModel.id == criteria.classroom_id))
        stmt = apply_name_gender_filters(stmt, TeacherModel, criteria)
        rows, total = await self._paginate(stmt, offset, limit)
        return [_to_entity(m) for m in rows], total

    async def exists_in_classroom_from_other_school(self, classroom_id: int, school_id: int) -> bool:
        stmt = (
            select(teacher_classrooms.c.teacher_id)
            .join(TeacherModel, TeacherModel.id == teacher_classrooms.c.teacher_id)
            .where(
                teacher_classrooms.c.classroom_id == classroom_id,
                TeacherModel.school_id != school_id,
            )
            .limit(1)
        )
        return await self.session.scalar(stmt) is not None
