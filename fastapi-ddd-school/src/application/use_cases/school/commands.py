from dataclasses import asdict, replace
from typing import Any

from src.application.dto.inputs import SchoolInput
from src.application.use_cases.base import UseCase, get_or_404
from src.domain.entities.school import School


class CreateSchool(UseCase):
    async def execute(self, data: SchoolInput) -> School:
        school = await self.uow.schools.save(School(**asdict(data)))
        await self.uow.commit()
        return school


class UpdateSchool(UseCase):
    async def execute(self, school_id: int, changes: dict[str, Any]) -> School:
        current: School = await get_or_404(self.uow.schools, school_id, "School")
        school = await self.uow.schools.save(replace(current, **changes))
        await self.uow.commit()
        return school


class DeleteSchool(UseCase):
    """Deleting a school cascades to its classrooms, teachers and students."""

    async def execute(self, school_id: int) -> None:
        await get_or_404(self.uow.schools, school_id, "School")
        await self.uow.schools.delete(school_id)
        await self.uow.commit()
