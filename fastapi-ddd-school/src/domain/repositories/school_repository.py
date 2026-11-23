from abc import ABC, abstractmethod

from src.domain.entities.school import School, SchoolStats


class SchoolRepository(ABC):
    @abstractmethod
    async def get(self, school_id: int) -> School | None: ...

    @abstractmethod
    async def save(self, school: School) -> School:
        """Insert when ``school.id`` is None, otherwise update."""

    @abstractmethod
    async def delete(self, school_id: int) -> None: ...

    @abstractmethod
    async def search(
        self, *, name: str | None = None, offset: int = 0, limit: int | None = None
    ) -> tuple[list[School], int]:
        """Return (page of schools, total matching)."""

    @abstractmethod
    async def get_stats(self, school_id: int) -> SchoolStats: ...
