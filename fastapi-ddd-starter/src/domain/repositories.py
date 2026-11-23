from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities import School, SchoolCounts


class SchoolRepository(ABC):
    @abstractmethod
    def add(self, school: School) -> School:
        ...

    @abstractmethod
    def get(self, school_id: int) -> Optional[School]:
        ...

    @abstractmethod
    def list(self, name: Optional[str] = None) -> list[School]:
        ...

    @abstractmethod
    def update(self, school: School) -> School:
        """Raises SchoolNotFoundError if the school does not exist."""

    @abstractmethod
    def delete(self, school_id: int) -> None:
        """Raises SchoolNotFoundError if the school does not exist."""

    @abstractmethod
    def counts(self, school_id: int) -> SchoolCounts:
        ...
