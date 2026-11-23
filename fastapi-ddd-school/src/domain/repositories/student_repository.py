from abc import ABC, abstractmethod

from src.domain.entities.student import Student
from src.domain.repositories.criteria import PersonCriteria


class StudentRepository(ABC):
    @abstractmethod
    async def get(self, student_id: int) -> Student | None: ...

    @abstractmethod
    async def save(self, student: Student) -> Student: ...

    @abstractmethod
    async def delete(self, student_id: int) -> None: ...

    @abstractmethod
    async def search(
        self, criteria: PersonCriteria, *, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Student], int]: ...
