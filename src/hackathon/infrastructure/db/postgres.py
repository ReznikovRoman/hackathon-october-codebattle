from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import UUID

from orjson import dumps, loads
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from starlite import Starlite

from hackathon.config.settings import DatabaseSettings
from hackathon.lib.exceptions import ConflictError
from hackathon.lib.repositories.exceptions import RepositoryError

if TYPE_CHECKING:
    from hackathon.lib.repositories.types import SessionFactory

__all__ = ["Database"]


def _default(value: Any) -> str:
    if isinstance(value, UUID):
        return str(value)
    raise TypeError()


def _sqla_on_connect(dbapi_connection: Any, _: Any) -> Any:
    """Using orjson for serialization of the json column values means that the output is binary,
    not `str` like `json.dumps` would output.

    SQLAlchemy expects that the json serializer returns `str` and calls `.encode()` on the value to
    turn it to bytes before writing to the JSONB column. We'd need to either wrap `orjson.dumps` to
    return a `str` so that SQLAlchemy could then convert it to binary, or do the following, which
    changes the behaviour of the dialect to expect a binary value from the serializer.

    See Also: https://github.com/sqlalchemy/sqlalchemy/blob/14bfbadfdf9260a1c40f63b31641b27fe9de12a0/lib/sqlalchemy/dialects/postgresql/asyncpg.py#L934  # noqa
    """

    def encoder(bin_value: bytes) -> bytes:
        # \x01 is the prefix for jsonb used by PostgreSQL.
        # asyncpg requires it when format='binary'
        return b"\x01" + bin_value

    def decoder(bin_value: bytes) -> Any:
        # the byte is the \x01 prefix for jsonb used by PostgreSQL.
        # asyncpg returns it when format='binary'
        return loads(bin_value[1:])

    dbapi_connection.await_(
        dbapi_connection.driver_connection.set_type_codec(
            "jsonb",
            encoder=encoder,
            decoder=decoder,
            schema="pg_catalog",
            format="binary",
        ),
    )


class Database:
    """SQLAlchemy ORM wrapper."""

    def __init__(self, config: DatabaseSettings) -> None:
        self._engine = create_async_engine(
            config.URL,
            echo=config.ECHO,
            echo_pool=config.ECHO_POOL,
            json_serializer=partial(dumps, default=_default),
            max_overflow=config.POOL_MAX_OVERFLOW,
            pool_size=config.POOL_SIZE,
            pool_timeout=config.POOL_TIMEOUT,
            poolclass=NullPool if config.POOL_DISABLE else None,
        )
        self._async_session_factory = async_scoped_session(
            session_factory=async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession),
            scopefunc=asyncio.current_task,
        )

        self.register_events()

    def register_events(self) -> None:
        """Register SQLAlchemy events."""
        event.listen(self._engine.sync_engine, "connect", _sqla_on_connect)

    @asynccontextmanager
    async def session(self) -> SessionFactory:
        session: AsyncSession = self._async_session_factory()
        try:
            print("SESSION: OPEN")
            yield session
        except IntegrityError as exc:
            print("SESSION: EXCEPTION")
            await session.rollback()
            raise ConflictError from exc
        except SQLAlchemyError as exc:
            print("SESSION: EXCEPTION")
            await session.rollback()
            raise RepositoryError(f"An exception occurred: {exc}") from exc
        except Exception as exc:
            print("SESSION: EXCEPTION")
            logging.exception("Session rollback because of exception.")
            await session.rollback()
            raise RepositoryError(f"An exception occurred: {exc}") from exc
        finally:
            print("SESSION: CLOSE")
            await session.close()


async def get_db(config: DatabaseSettings, app: Starlite):
    _engine = create_async_engine(
        config.URL,
        echo=config.ECHO,
        echo_pool=config.ECHO_POOL,
        json_serializer=partial(dumps, default=_default),
        max_overflow=config.POOL_MAX_OVERFLOW,
        pool_size=config.POOL_SIZE,
        pool_timeout=config.POOL_TIMEOUT,
        poolclass=NullPool if config.POOL_DISABLE else None,
    )
    _async_session_factory = async_scoped_session(
        session_factory=async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession),
        scopefunc=asyncio.current_task,
    )
    session: AsyncSession = _async_session_factory()
    setattr(app.state, "_sqlalchemy_repository_session", session)
    yield session
    delattr(app.state, "_sqlalchemy_repository_session")
    await session.close()


class Repo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self):
        print("REPO")
        return (await self.session.execute(text("XXX"))).scalar_one()


class Service:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    async def execute(self):
        print("SERVICE")
        return await self.repo.get() == 1
