"""DTO implementation.

Using this implementation instead of the `starlite.SQLAlchemy` plugin DTO as
a POC for using the SQLAlchemy model type annotations to build the pydantic
model.

Also experimenting with marking columns for DTO purposes using the
`SQLAlchemy.Column.info` field, which allows demarcation of fields that
should always be private, or read-only at the model declaration layer.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Union, cast, get_args, get_origin, get_type_hints

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, Relationship

from starlite import DTOFactory

from .sqlalchemy_plugin import plugin

if TYPE_CHECKING:
    from sqlalchemy import Column
    from sqlalchemy.orm import DeclarativeBase, Mapper

DTO_INFO_KEY = "dto"

dto_factory = DTOFactory(plugins=[plugin])


class Mode(Enum):
    """SQLAlchemy field access mode."""

    read_only = auto()
    private = auto()


class Purpose(Enum):
    """DTO model access purpose/mode."""

    read = auto()
    write = auto()


def _construct_field_info(column: Union["Column", Relationship], purpose: Purpose) -> FieldInfo:
    if isinstance(column, Relationship):
        return FieldInfo(...)
    default = column.default
    if purpose is Purpose.read or default is None:
        return FieldInfo(...)
    if default.is_scalar:
        return FieldInfo(default=default.arg)
    if default.is_callable:
        return FieldInfo(default_factory=lambda: default.arg({}))
    raise ValueError("Unexpected default type")


def _should_exclude_field(purpose: Purpose, column: "Column", exclude: set[str]) -> bool:
    if column.key in exclude:
        return True
    mode = column.info.get(DTO_INFO_KEY)
    if mode is Mode.private:
        return True
    if purpose is Purpose.write and mode is Mode.read_only:
        return True
    return False


class Config:
    orm_mode = True


def factory(
    name: str, model: type["DeclarativeBase"], purpose: Purpose, exclude: set[str] | None = None,
    *,
    with_relationships: bool = True,
) -> type[BaseModel]:
    """Create a pydantic model class from a SQLAlchemy declarative ORM class.

    The fields that are included in the model can be controlled on the SQLAlchemy class
    definition by including a "dto" key in the `Column.info` mapping. For example:

        ```python
        class User(DeclarativeBase):
            id: Mapped[UUID] = mapped_column(
                default=uuid4, primary_key=True, info={"dto": dto.Mode.read_only}
            )
            email: Mapped[str]
            password_hash: Mapped[str] = mapped_column(info={"dto": dto.Mode.private})
        ```

    In the above example, a DTO generated for `Purpose.read` will include the `id` and `email` fields,
    while a model generated for `Purpose.write` will only include a field for `email`. Notice that
    columns marked as `Mode.private` will not have a field produced in any DTO object.

    Args:
        name: Name given to the DTO class.
        model: The SQLAlchemy model class.
        purpose: Is the DTO for write or read operations?
        exclude: Explicitly exclude attributes from the DTO.
        with_relationships: Create DTO for relationships?

    Returns:
        A Pydantic model that includes only fields that are appropriate to `purpose` and not in `exclude`.
    """
    exclude = exclude or set[str]()
    mapper = cast("Mapper", inspect(model))
    columns = mapper.columns
    dto_fields: dict[str, tuple[Any, FieldInfo]] = {}
    for key, type_hint in get_type_hints(model).items():
        if get_origin(type_hint) is not Mapped:
            continue
        if relationship := cast("Mapper", mapper.relationships.get(key)):
            if not with_relationships or _should_exclude_field(purpose, relationship, exclude):
                continue
            relationship_dto = handle_relationship(name, relationship, purpose=purpose, exclude=exclude)
            dto_fields[key] = (list[relationship_dto] | Any, FieldInfo(...))
            continue
        column = columns[key]
        if _should_exclude_field(purpose, column, exclude):
            continue
        (type_,) = get_args(type_hint)
        dto_fields[key] = (type_, _construct_field_info(column, purpose))
    return create_model(  # type:ignore[no-any-return,call-overload]
        name, __config__=type("Config", (), {"orm_mode": True}), **dto_fields,
    )


def handle_relationship(
    base_name: str, relationship: "Mapper", purpose: Purpose, exclude: set[str] | None = None,
) -> type[BaseModel]:
    relationship_class = relationship.mapper.class_
    relationship_dto = factory(
        f"{relationship_class.__name__}{base_name}", relationship_class,
        purpose=purpose, exclude=exclude, with_relationships=False,
    )
    return relationship_dto
