from collections import abc
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from sqlalchemy import select, text
from sqlalchemy.engine import Result

from .abc import AbstractRepository
from .filters import BeforeAfter, CollectionFilter, LimitOffset, SearchFilter

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

    from .. import orm
    from .types import FilterTypes, SessionFactory

__all__ = [
    "SQLAlchemyRepository",
    "ModelT",
]

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound="orm.Base")


class SQLAlchemyRepository(AbstractRepository[ModelT]):
    """SQLAlchemy based repository."""

    model_type: type[ModelT]

    def __init__(
        self,
        session_factory: "SessionFactory",
        select_: "Select[tuple[ModelT]] | None" = None,
    ) -> None:
        self._session_factory = session_factory
        self._select = select(self.model_type) if select_ is None else select_

    async def add(self, data: ModelT) -> ModelT:
        async with self._session_factory() as session:
            instance = await self._attach_to_session(session, model=data)
            await session.refresh(instance)
            session.expunge(instance)
            return instance

    async def delete(self, id_: Any) -> ModelT:
        async with self._session_factory() as session:
            instance = await self.get(id_)
            await session.delete(instance)
            await session.commit()
            session.expunge(instance)
            return instance

    async def get(self, id_: Any) -> ModelT:
        async with self._session_factory() as session:
            self._filter_select_by_kwargs(**{self.id_attribute: id_})
            self.before_get_execute(session, id_)
            instance = (await self._execute(session)).scalar_one_or_none()
            instance = self.check_not_found(instance)
            session.expunge(instance)
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

        async with self._session_factory() as session:
            self.before_list_execute(session, *filters, **kwargs)
            result = await self._execute(session)
            instances = list(result.scalars())
            for instance in instances:
                session.expunge(instance)
            return instances

    async def update(self, data: ModelT) -> ModelT:
        async with self._session_factory() as session:
            id_ = self.get_id_attribute_value(data)
            # this will raise for not found, and will put the item in the session
            await self.get(id_)
            # this will merge the inbound data to the instance we've just put in the session
            instance = await self._attach_to_session(session, model=data, strategy="merge")
            await session.refresh(instance)
            session.expunge(instance)
            return instance

    async def upsert(self, data: ModelT) -> ModelT:
        async with self._session_factory() as session:
            instance = await self._attach_to_session(session, model=data, strategy="merge")
            await session.refresh(instance)
            session.expunge(instance)
            return instance

    def before_get_execute(self, session: "AsyncSession", id_: Any) -> None:
        """Perform an action before executing `get` method.

        For example:
            ```python
            def before_get_execute(self, id_: Any) -> None:
                self._session = self._session.options(selectinload(Author.books))
            ```
        """

    def before_list_execute(self, session: "AsyncSession", *filters: "FilterTypes", **kwargs: Any) -> None:
        """Perform an action before executing `list` method.

        For example:
            ```python
            def before_list_execute(self, *filters: "FilterTypes", **kwargs: Any) -> None:
                self._session = self._session.options(selectinload(Author.books))
            ```
        """

    @classmethod
    async def check_health(cls, session_factory: "SessionFactory") -> bool:
        """Perform a health check on the database.

        Args:
            session_factory: scoped session factory that creates a session through which we run a check statement.

        Returns:
            `True` if healthy.
        """
        async with session_factory() as session:
            return (await session.execute(text("SELECT 1"))).scalar_one() == 1

    # the following is all sqlalchemy implementation detail, and shouldn't be directly accessed

    def _apply_limit_offset_pagination(self, limit: int, offset: int) -> None:
        self._select = self._select.limit(limit).offset(offset)

    async def _attach_to_session(
        self,
        session: "AsyncSession", *,
        model: ModelT,
        strategy: Literal["add", "merge"] = "add",
    ) -> ModelT:
        """Attach detached instance to the session.

        Args:
            model: The instance to be attached to the session.
            strategy: How the instance should be attached.

        Returns:
            The attached instance.
        """
        match strategy:
            case "add":
                session.add(model)
            case "merge":
                model = await session.merge(model)
        await session.commit()
        return model

    async def _execute(self, session: "AsyncSession") -> Result[tuple[ModelT, ...]]:
        return await session.execute(self._select)

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
