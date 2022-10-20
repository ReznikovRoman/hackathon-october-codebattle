from enum import Enum, auto


class Mode(Enum):
    """SQLAlchemy field access mode."""

    read_only = auto()
    private = auto()


class Purpose(Enum):
    """DTO model access purpose/mode."""

    read = auto()
    write = auto()
