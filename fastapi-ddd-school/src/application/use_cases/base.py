from typing import Any, Protocol, TypeVar

from src.application.unit_of_work import UnitOfWork
from src.core.exceptions import BusinessRuleError, NotFoundError

T = TypeVar("T", covariant=True)


class _Getter(Protocol[T]):
    async def get(self, entity_id: int, /) -> T | None: ...


class UseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow


async def get_or_404(repository: _Getter[Any], entity_id: int, label: str) -> Any:
    """Load the resource addressed by the URL or raise NotFoundError (404)."""
    entity = await repository.get(entity_id)
    if entity is None:
        raise NotFoundError(f"{label} {entity_id} not found")
    return entity


async def ensure_reference(repository: _Getter[Any], entity_id: int, label: str) -> None:
    """A referenced id in the request body must exist (422, not 404)."""
    if await repository.get(entity_id) is None:
        raise BusinessRuleError(f"{label} {entity_id} does not exist")
