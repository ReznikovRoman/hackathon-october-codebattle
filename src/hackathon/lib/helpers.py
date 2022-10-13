import re
from typing import Any, Iterator
from zoneinfo import ZoneInfo

SLUG_REGEX = re.compile(r"^[-\w]+$")

TZ_MOSCOW = ZoneInfo("Europe/Moscow")

sentinel: Any = object()


def resolve_callables(mapping: dict) -> Iterator[tuple[Any, Any]]:
    """Generate key-value pairs from mapping, where values can be `callable` objects."""
    for key, value in mapping.items():
        yield key, value() if callable(value) else value
