from collections import abc
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from sqlalchemy import select, text
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..exceptions import ConflictError
from .abc import AbstractRepository
from .exceptions import RepositoryException
from .filters import BeforeAfter, CollectionFilter, LimitOffset, SearchFilter

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

    from .. import orm
    from .types import FilterTypes

__all__ = [
    "SQLAlchemyRepository",
    "ModelT",
]

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound="orm.Base")


@contextmanager
def wrap_sqlalchemy_exception() -> Any:
    """Do something within context to raise a `RepositoryException` chained from an original `SQLAlchemyError`.

    >>> try:
    ...     with wrap_sqlalchemy_exception():
    ...         raise SQLAlchemyError("Original Exception")
    ... except RepositoryException as exc:
    ...     print(f"caught repository exception from {type(exc.__context__)}")
    ...
    caught repository exception from <class 'sqlalchemy.exc.SQLAlchemyError'>
    """
    try:
        yield
    except IntegrityError as e:
        raise ConflictError from e
    except SQLAlchemyError as e:
        raise RepositoryException(f"An exception occurred: {e}") from e


class SQLAlchemyRepository(AbstractRepository[ModelT]):
    """SQLAlchemy based repository."""

    model_type: type[ModelT]

    def __init__(self, session: "AsyncSession", select_: "Select[tuple[ModelT]] | None" = None) -> None:
        self._session = session
        self._select = select(self.model_type) if select_ is None else select_

    async def add(self, data: ModelT) -> ModelT:
        with wrap_sqlalchemy_exception():
            instance = await self._attach_to_session(data)
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    async def delete(self, id_: Any) -> ModelT:
        with wrap_sqlalchemy_exception():
            instance = await self.get(id_)
            await self._session.delete(instance)
            await self._session.flush()
            self._session.expunge(instance)
            return instance

    async def get(self, id_: Any) -> ModelT:
        with wrap_sqlalchemy_exception():
            self._filter_select_by_kwargs(**{self.id_attribute: id_})
            instance = (await self._execute()).scalar_one_or_none()
            instance = self.check_not_found(instance)
            self._session.expunge(instance)
            return instance

    async def list(self, *filters: "FilterTypes", **kwargs: Any) -> list[ModelT]:
        for filter_ in filters:
            match filter_:
                case LimitOffset(limit, offset):
                    self._apply_limit_offset_pagination(limit, offset)  # noqa: F821
                case BeforeAfter(field_name, before, after):
                    self._filter_on_datetime_field(field_name, before, after)  # noqa: F821
                case CollectionFilter(field_name, values):
                    self._filter_in_collection(field_name, values)  # noqa: F821
                case SearchFilter(field_name, query):
                    self._filter_like_collection(field_name, query)  # noqa: F821
        self._filter_select_by_kwargs(**kwargs)

        with wrap_sqlalchemy_exception():
            result = await self._execute()
            instances = list(result.scalars())
            for instance in instances:
                self._session.expunge(instance)
            return instances

    async def update(self, data: ModelT) -> ModelT:
        with wrap_sqlalchemy_exception():
            id_ = self.get_id_attribute_value(data)
            # this will raise for not found, and will put the item in the session
            await self.get(id_)
            # this will merge the inbound data to the instance we've just put in the session
            instance = await self._attach_to_session(data, strategy="merge")
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    async def upsert(self, data: ModelT) -> ModelT:
        with wrap_sqlalchemy_exception():
            instance = await self._attach_to_session(data, strategy="merge")
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    @classmethod
    async def check_health(cls, db_session: "AsyncSession") -> bool:
        """Perform a health check on the database.

        Args:
            db_session: session through which we run a check statement.

        Returns:
            `True` if healthy.
        """
        return (await db_session.execute(text("SELECT 1"))).scalar_one() == 1

    # the following is all sqlalchemy implementation detail, and shouldn't be directly accessed

    def _apply_limit_offset_pagination(self, limit: int, offset: int) -> None:
        self._select = self._select.limit(limit).offset(offset)

    async def _attach_to_session(self, model: ModelT, strategy: Literal["add", "merge"] = "add") -> ModelT:
        """Attach detached instance to the session.

        Args:
            model: The instance to be attached to the session.
            strategy: How the instance should be attached.

        Returns:
            The attached instance.
        """
        match strategy:
            case "add":
                self._session.add(model)
            case "merge":
                model = await self._session.merge(model)
        return model

    async def _execute(self) -> Result[tuple[ModelT, ...]]:
        return await self._session.execute(self._select)

    def _filter_in_collection(self, field_name: str, values: abc.Collection[Any]) -> None:
        if not values:
            return
        self._select = self._select.where(getattr(self.model_type, field_name).in_(values))

    def _filter_like_collection(self, field_name: str, query: str | None = None) -> None:
        if query is None:
            return
        self._select = self._select.where(getattr(self.model_type, field_name).like("%{query}%".format(query=query)))

    def _filter_on_datetime_field(self, field_name: str, before: "datetime | None", after: "datetime | None") -> None:
        field = getattr(self.model_type, field_name)
        if before is not None:
            self._select = self._select.where(field < before)
        if after is not None:
            self._select = self._select.where(field > before)

    def _filter_select_by_kwargs(self, **kwargs: Any) -> None:
        for field, value in kwargs.items():
            self._select = self._select.where(getattr(self.model_type, field) == value)
