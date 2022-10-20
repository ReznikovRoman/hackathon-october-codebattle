from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Callable

from .filters import BeforeAfter, CollectionFilter, LimitOffset, SearchFilter

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

FilterTypes = BeforeAfter | CollectionFilter | SearchFilter | LimitOffset
SessionFactory = Callable[..., AbstractAsyncContextManager["AsyncSession"]]
