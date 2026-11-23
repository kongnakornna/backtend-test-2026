from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.core.config import get_settings


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _record: Any) -> None:
    # SQLite ignores FOREIGN KEY / ON DELETE CASCADE unless this is on per connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_engine(url: str, echo: bool = False, **kwargs: Any) -> AsyncEngine:
    engine = create_async_engine(url, echo=echo, **kwargs)
    if engine.dialect.name == "sqlite":
        event.listen(engine.sync_engine, "connect", _enable_sqlite_foreign_keys)
    return engine


_settings = get_settings()
engine = build_engine(_settings.database_url, echo=_settings.sql_echo)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
