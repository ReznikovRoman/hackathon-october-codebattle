from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from .filters import BeforeAfter, CollectionFilter, LimitOffset, SearchFilter

FilterTypes = BeforeAfter | CollectionFilter | SearchFilter | LimitOffset
SessionFactory = Callable[..., AbstractAsyncContextManager[AsyncSession]]
