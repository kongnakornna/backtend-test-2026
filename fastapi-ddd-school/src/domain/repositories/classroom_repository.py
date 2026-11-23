from abc import ABC, abstractmethod

from src.domain.entities.classroom import Classroom


class ClassroomRepository(ABC):
    @abstractmethod
    async def get(self, classroom_id: int) -> Classroom | None: ...

    @abstractmethod
    async def get_many(self, classroom_ids: list[int]) -> list[Classroom]:
        """Return the classrooms that exist among ``classroom_ids``, ordered by id."""

    @abstractmethod
    async def save(self, classroom: Classroom) -> Classroom: ...

    @abstractmethod
    async def delete(self, classroom_id: int) -> None: ...

    @abstractmethod
    async def search(
        self, *, school_id: int | None = None, offset: int = 0, limit: int | None = None
    ) -> tuple[list[Classroom], int]: ...

    @abstractmethod
    async def exists_duplicate(
        self, school_id: int, year_level: int, section: str, exclude_id: int | None = None
    ) -> bool:
        """True when another classroom in the school has the same year_level/section."""
