from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
