from dataclasses import asdict, replace
from typing import Any

from src.application.dto.inputs import StudentInput
from src.application.use_cases.base import UseCase, ensure_reference, get_or_404
from src.domain.entities.student import Student


class CreateStudent(UseCase):
    async def execute(self, data: StudentInput) -> Student:
        student = Student(**asdict(data))
        await ensure_reference(self.uow.classrooms, student.classroom_id, "Classroom")
        saved = await self.uow.students.save(student)
        await self.uow.commit()
        return saved


class UpdateStudent(UseCase):
    async def execute(self, student_id: int, changes: dict[str, Any]) -> Student:
        current: Student = await get_or_404(self.uow.students, student_id, "Student")
        updated = replace(current, **changes)
        if updated.classroom_id != current.classroom_id:
            await ensure_reference(self.uow.classrooms, updated.classroom_id, "Classroom")
        saved = await self.uow.students.save(updated)
        await self.uow.commit()
        return saved


class DeleteStudent(UseCase):
    async def execute(self, student_id: int) -> None:
        await get_or_404(self.uow.students, student_id, "Student")
        await self.uow.students.delete(student_id)
        await self.uow.commit()
