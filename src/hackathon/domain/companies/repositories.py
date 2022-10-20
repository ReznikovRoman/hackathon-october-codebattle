from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import selectinload

from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

from .models import Company

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class CompanyRepository(SQLAlchemyRepository):
    """Repository for working with Companies data."""

    model_type = Company

    def before_get_execute(self, session: AsyncSession, id_: Any) -> None:
        self._select = self._select.select_from(Company).options(selectinload(Company.advocates))
