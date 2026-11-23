"""Composition root: the only presentation module that knows the infrastructure.

Routers depend on the abstract ``UnitOfWork``; this module decides which
implementation (SQLAlchemy) they get. Tests override ``get_session``.
"""

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.unit_of_work import UnitOfWork
from src.infrastructure.db.session import SessionFactory
from src.infrastructure.repositories.unit_of_work import SqlAlchemyUnitOfWork


async def get_session() -> AsyncIterator[AsyncSession]:
    # Leaving the context closes the session, rolling back anything not committed.
    async with SessionFactory() as session:
        yield session


def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)
