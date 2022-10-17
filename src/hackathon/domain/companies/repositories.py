from typing import Any

from sqlalchemy.orm import selectinload

from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

from .models import Company


class CompanyRepository(SQLAlchemyRepository):
    """Repository for working with Companies data."""

    model_type = Company

    def before_get_execute(self, id_: Any) -> None:
        self._select = self._select.select_from(Company).options(selectinload(Company.advocates))
