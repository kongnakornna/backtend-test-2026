from abc import ABC, abstractmethod

from src.domain.entities.teacher import Teacher
from src.domain.repositories.criteria import PersonCriteria


class TeacherRepository(ABC):
    @abstractmethod
    async def get(self, teacher_id: int) -> Teacher | None: ...

    @abstractmethod
    async def save(self, teacher: Teacher) -> Teacher:
        """Persist the teacher including its classroom assignments."""

    @abstractmethod
    async def delete(self, teacher_id: int) -> None: ...

    @abstractmethod
    async def search(
        self, criteria: PersonCriteria, *, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Teacher], int]: ...

    @abstractmethod
    async def exists_in_classroom_from_other_school(self, classroom_id: int, school_id: int) -> bool:
        """True when the classroom has a teacher whose school is not ``school_id``."""
