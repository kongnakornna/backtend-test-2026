from sqlalchemy import delete, select

from src.core.exceptions import NotFoundError
from src.domain.entities.classroom import Classroom
from src.domain.repositories.classroom_repository import ClassroomRepository
from src.infrastructure.models import ClassroomModel
from src.infrastructure.repositories.base import SqlAlchemyRepository


def _to_entity(model: ClassroomModel) -> Classroom:
    return Classroom(
        id=model.id, school_id=model.school_id, year_level=model.year_level, section=model.section
    )


class SqlAlchemyClassroomRepository(SqlAlchemyRepository, ClassroomRepository):
    async def get(self, classroom_id: int) -> Classroom | None:
        model = await self.session.get(ClassroomModel, classroom_id)
        return _to_entity(model) if model else None

    async def get_many(self, classroom_ids: list[int]) -> list[Classroom]:
        if not classroom_ids:
            return []
        rows = await self.session.scalars(
            select(ClassroomModel)
            .where(ClassroomModel.id.in_(classroom_ids))
            .order_by(ClassroomModel.id)
        )
        return [_to_entity(m) for m in rows]

    async def save(self, classroom: Classroom) -> Classroom:
        if classroom.id is None:
            model = ClassroomModel()
            self.session.add(model)
        else:
            model = await self.session.get(ClassroomModel, classroom.id)
            if model is None:
                raise NotFoundError(f"Classroom {classroom.id} not found")
        model.school_id = classroom.school_id
        model.year_level = classroom.year_level
        model.section = classroom.section
        await self._flush()
        return _to_entity(model)

    async def delete(self, classroom_id: int) -> None:
        await self.session.execute(delete(ClassroomModel).where(ClassroomModel.id == classroom_id))

    async def search(
        self, *, school_id: int | None = None, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Classroom], int]:
        stmt = select(ClassroomModel).order_by(ClassroomModel.id)
        if school_id is not None:
            stmt = stmt.where(ClassroomModel.school_id == school_id)
        rows, total = await self._paginate(stmt, offset, limit)
        return [_to_entity(m) for m in rows], total

    async def exists_duplicate(
        self, school_id: int, year_level: int, section: str, exclude_id: int | None = None
    ) -> bool:
        stmt = select(ClassroomModel.id).where(
            ClassroomModel.school_id == school_id,
            ClassroomModel.year_level == year_level,
            ClassroomModel.section == section,
        )
        if exclude_id is not None:
            stmt = stmt.where(ClassroomModel.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None
