from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as exc:  # e.g. a concurrent duplicate insert
            raise ConflictError("The data conflicts with an existing record") from exc

    async def _paginate(
        self, stmt: Select[Any], offset: int, limit: int | None
    ) -> tuple[list[Any], int]:
        total = await self.session.scalar(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        rows = (await self.session.scalars(stmt.offset(offset))).all()
        return list(rows), total or 0
