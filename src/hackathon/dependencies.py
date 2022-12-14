import datetime
import uuid
from typing import Callable, Final, Sequence, TypeAlias

from starlite import Dependency, Parameter, Provide

from hackathon.config.settings import get_settings
from hackathon.lib.repositories.filters import BeforeAfter, CollectionFilter, LimitOffset, SearchFilter
from hackathon.lib.repositories.types import FilterTypes

DTorNone: TypeAlias = datetime.datetime | None

FILTERS_DEPENDENCY_KEY: Final[str] = "filters"
CREATED_FILTER_DEPENDENCY_KEY: Final[str] = "created_filter"
UPDATED_FILTER_DEPENDENCY_KEY: Final[str] = "updated_filter"
ID_FILTER_DEPENDENCY_KEY: Final[str] = "id_filter"
SEARCH_FILTER_DEPENDENCY_KEY: Final[str] = "search_filter"
LIMIT_OFFSET_DEPENDENCY_KEY: Final[str] = "limit_offset"

settings = get_settings()


def search_filter_provider_factory(field_names: Sequence[str]) -> Callable[[str], SearchFilter[uuid.UUID]]:
    """Build `SearchFilter` provider.

    Args:
        field_names: Names of model attributes to filter on.
    """

    def provide_search_filter(
        q: str | None = Parameter(query="q", default=None, required=False),  # noqa: VNE001
    ) -> SearchFilter[uuid.UUID]:
        """Return type consumed by `Repository.filter_like_collection()`.

        Args:
            q: Parsed out of comma separated list of values in query params.
        """
        query = q
        if query is not None:
            query = query.strip()
        return SearchFilter(field_names=field_names, query=query)

    return provide_search_filter


def provide_id_filter(
    ids: list[uuid.UUID] | None = Parameter(query="ids", default=None, required=False),
) -> CollectionFilter[uuid.UUID]:
    """Return type consumed by `Repository.filter_in_collection()`.

    Args:
        ids: Parsed out of comma separated list of values in query params.
    """
    return CollectionFilter(field_name="id", values=ids or [])


def provide_created_filter(
    before: DTorNone = Parameter(query="created-before", default=None, required=False),
    after: DTorNone = Parameter(query="created-after", default=None, required=False),
) -> BeforeAfter:
    """Return type consumed by `Repository.filter_on_datetime_field()`.

    Args:
        before: Filter for records updated before this date/time.
        after: Filter for records updated after this date/time.
    """
    return BeforeAfter("created_at", before, after)


def provide_updated_filter(
    before: DTorNone = Parameter(query="updated-before", default=None, required=False),
    after: DTorNone = Parameter(query="updated-after", default=None, required=False),
) -> BeforeAfter:
    """Return type consumed by `Repository.filter_on_datetime_field()`.

    Args:
        before: Filter for records updated before this date/time.
        after: Filter for records updated after this date/time.
    """
    return BeforeAfter("updated_at", before, after)


def provide_limit_offset_pagination(
    page: int = Parameter(ge=1, default=1, required=False),
    page_size: int = Parameter(
        query="page-size",
        ge=1,
        default=settings.api.DEFAULT_PAGINATION_LIMIT,
        required=False,
    ),
) -> LimitOffset:
    """Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Args:
        page: LIMIT to apply to select.
        page_size: OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (page - 1))


def provide_filter_dependencies(
    created_filter: BeforeAfter = Dependency(skip_validation=True),
    updated_filter: BeforeAfter = Dependency(skip_validation=True),
    id_filter: CollectionFilter = Dependency(skip_validation=True),
    limit_offset: LimitOffset = Dependency(skip_validation=True),
) -> list[FilterTypes]:
    """Common collection route filtering dependencies.

    Add all filters to any route by including this function as a dependency, e.g:

        @get
        def get_collection_handler(filters: Filters) -> ...:
            ...

    The dependency is provided at the application layer, so only need to inject the dependency where necessary.

    Args:
        id_filter: Filter for scoping query to limited set of identities.
        created_filter: Filter for scoping query to instance creation date/time.
        updated_filter: Filter for scoping query to instance update date/time.
        limit_offset: Filter for query pagination.

    Returns:
        List of filters parsed from connection.
    """
    return [
        created_filter,
        id_filter,
        limit_offset,
        updated_filter,
    ]


def create_collection_dependencies() -> dict[str, Provide]:
    """Creates a dictionary of provides for pagination endpoints."""
    return {
        LIMIT_OFFSET_DEPENDENCY_KEY: Provide(provide_limit_offset_pagination),
        UPDATED_FILTER_DEPENDENCY_KEY: Provide(provide_updated_filter),
        CREATED_FILTER_DEPENDENCY_KEY: Provide(provide_created_filter),
        ID_FILTER_DEPENDENCY_KEY: Provide(provide_id_filter),
        FILTERS_DEPENDENCY_KEY: Provide(provide_filter_dependencies),
    }


def create_project_dependencies() -> dict[str, Provide]:
    """Create project dependencies."""
    dependencies = {
        settings.api.CONFIG_DEPENDENCY_KEY: Provide(get_settings),
    }
    dependencies.update(create_collection_dependencies())
    return dependencies
