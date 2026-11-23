from dataclasses import replace
from typing import Any

from src.application.dto.inputs import TeacherInput
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.base import UseCase, ensure_reference, get_or_404
from src.core.exceptions import BusinessRuleError
from src.domain.entities.teacher import Teacher


async def _assign_classrooms(uow: UnitOfWork, teacher: Teacher, classroom_ids: list[int]) -> None:
    wanted = sorted(set(classroom_ids))
    classrooms = await uow.classrooms.get_many(wanted) if wanted else []
    missing = sorted(set(wanted) - {c.id for c in classrooms})
    if missing:
        raise BusinessRuleError(f"Classrooms {missing} do not exist")
    teacher.assign_classrooms(classrooms)  # enforces the same-school rule


class CreateTeacher(UseCase):
    async def execute(self, data: TeacherInput) -> Teacher:
        teacher = Teacher(
            school_id=data.school_id,
            first_name=data.first_name,
            last_name=data.last_name,
            gender=data.gender,
        )
        await ensure_reference(self.uow.schools, teacher.school_id, "School")
        await _assign_classrooms(self.uow, teacher, data.classroom_ids)
        saved = await self.uow.teachers.save(teacher)
        await self.uow.commit()
        return saved


class UpdateTeacher(UseCase):
    async def execute(self, teacher_id: int, changes: dict[str, Any]) -> Teacher:
        current: Teacher = await get_or_404(self.uow.teachers, teacher_id, "Teacher")
        changes = dict(changes)
        classroom_ids = changes.pop("classroom_ids", current.classroom_ids)
        updated = replace(current, **changes)

        if updated.school_id != current.school_id:
            await ensure_reference(self.uow.schools, updated.school_id, "School")
        # Re-check even when only the school changed: kept classrooms must match it.
        await _assign_classrooms(self.uow, updated, classroom_ids)

        saved = await self.uow.teachers.save(updated)
        await self.uow.commit()
        return saved


class DeleteTeacher(UseCase):
    async def execute(self, teacher_id: int) -> None:
        await get_or_404(self.uow.teachers, teacher_id, "Teacher")
        await self.uow.teachers.delete(teacher_id)
        await self.uow.commit()
