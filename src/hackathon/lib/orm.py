from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.event import listens_for
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, declared_attr, mapped_column, registry

from . import dto

if TYPE_CHECKING:
    from pydantic import BaseModel

BaseT = TypeVar("BaseT", bound="Base")

# Templates for automated constraint name generation
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


@listens_for(Session, "before_flush")
def touch_updated_timestamp(session: Session, *_: Any) -> None:
    """Called from SQLAlchemy's `before_flush` event to bump the `updated_at` timestamp on modified instances.

    Args:
        session: The sync `sqlalchemy.orm.Session` instance that underlies the async session.
    """
    for instance in session.dirty:
        instance.updated_at = datetime.now()


class Base(DeclarativeBase):
    """Base for all SQLAlchemy declarative models.

    Attributes:
        created_at: Date/time of instance creation.
        updated_at: Date/time of last instance update.
    """

    registry = registry(
        metadata=MetaData(naming_convention=convention),
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True, info={"dto": dto.Mode.read_only})  # noqa: VNE003
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, info={"dto": dto.Mode.read_only})
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, info={"dto": dto.Mode.read_only})

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    @classmethod
    def from_dto(cls: type[BaseT], dto_instance: "BaseModel") -> BaseT:
        """Construct an instance of the SQLAlchemy model from the Pydantic DTO.

        Args:
            dto_instance: A pydantic model.

        Returns:
            An instance of the SQLAlchemy model.
        """
        return cls(**dto_instance.dict(exclude_unset=True))
