from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import joinedload

from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

from .models import Advocate, SocialAccount

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AdvocateRepository(SQLAlchemyRepository):
    """Repository for working with Advocates data."""

    model_type = Advocate

    def before_get_execute(self, session: AsyncSession, id_: Any) -> None:
        self._select = self._select.options(
            joinedload(Advocate.social_account),
            joinedload(Advocate.company),
        )


class SocialAccountRepository(SQLAlchemyRepository):
    """Repository for working with social accounts."""

    model_type = SocialAccount
