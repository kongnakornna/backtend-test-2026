from dataclasses import asdict, replace
from typing import Any

from src.application.dto.inputs import ClassroomInput
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.base import UseCase, ensure_reference, get_or_404
from src.core.exceptions import BusinessRuleError, ConflictError
from src.domain.entities.classroom import Classroom


async def _ensure_unique(uow: UnitOfWork, classroom: Classroom) -> None:
    if await uow.classrooms.exists_duplicate(
        classroom.school_id, classroom.year_level, classroom.section, exclude_id=classroom.id
    ):
        raise ConflictError(
            f"Classroom {classroom.year_level}/{classroom.section} "
            f"already exists in school {classroom.school_id}"
        )


class CreateClassroom(UseCase):
    async def execute(self, data: ClassroomInput) -> Classroom:
        classroom = Classroom(**asdict(data))
        await ensure_reference(self.uow.schools, classroom.school_id, "School")
        await _ensure_unique(self.uow, classroom)
        saved = await self.uow.classrooms.save(classroom)
        await self.uow.commit()
        return saved


class UpdateClassroom(UseCase):
    async def execute(self, classroom_id: int, changes: dict[str, Any]) -> Classroom:
        current: Classroom = await get_or_404(self.uow.classrooms, classroom_id, "Classroom")
        updated = replace(current, **changes)

        if updated.school_id != current.school_id:
            await ensure_reference(self.uow.schools, updated.school_id, "School")
            # Moving the room must not leave a teacher teaching outside their school.
            if await self.uow.teachers.exists_in_classroom_from_other_school(
                classroom_id, updated.school_id
            ):
                raise BusinessRuleError(
                    f"Cannot move classroom {classroom_id} to school {updated.school_id}: "
                    "it has teachers from another school"
                )

        await _ensure_unique(self.uow, updated)
        saved = await self.uow.classrooms.save(updated)
        await self.uow.commit()
        return saved


class DeleteClassroom(UseCase):
    """Deleting a classroom cascades to its students and teacher assignments."""

    async def execute(self, classroom_id: int) -> None:
        await get_or_404(self.uow.classrooms, classroom_id, "Classroom")
        await self.uow.classrooms.delete(classroom_id)
        await self.uow.commit()
