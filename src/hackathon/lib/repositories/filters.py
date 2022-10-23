from collections import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Sequence, TypeVar

T = TypeVar("T")


@dataclass
class BeforeAfter:
    """Data required to filter a query on a `datetime` column."""

    # Name of the model attribute to filter on
    field_name: str

    # Filter results where field earlier than this `datetime.datetime`
    before: datetime | None

    # Filter results where field later than this `datetime.datetime`
    after: datetime | None


@dataclass
class CollectionFilter(Generic[T]):
    """Data required to construct a `WHERE ... IN (...)` clause."""

    # Name of the model attribute to filter on
    field_name: str

    # Values for `IN` clause
    values: abc.Collection[T]


@dataclass
class SearchFilter(Generic[T]):
    """Data required to construct a `WHERE ... LIKE %...%` clause."""

    # Names of model attribute to filter on
    field_names: Sequence[str]

    # Search query for `LIKE` clause
    query: str


@dataclass
class LimitOffset:
    """Data required to add limit/offset filtering to a query."""

    # Value for `LIMIT` clause of query
    limit: int

    # Value for `OFFSET` clause of query
    offset: int
