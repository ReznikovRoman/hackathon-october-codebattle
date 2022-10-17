from typing import Any

from sqlalchemy.orm import joinedload

from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository, wrap_sqlalchemy_exception

from .models import Advocate, SocialAccount


class AdvocateRepository(SQLAlchemyRepository):
    """Repository for working with Advocates data."""

    model_type = Advocate

    async def get(self, id_: Any) -> Advocate:
        with wrap_sqlalchemy_exception():
            self._filter_select_by_kwargs(**{self.id_attribute: id_})
            self._select = self._select.options(joinedload(Advocate.social_account))
            instance = (await self._execute()).scalar_one_or_none()
            instance = self.check_not_found(instance)
            self._session.expunge(instance)
            return instance


class SocialAccountRepository(SQLAlchemyRepository):
    """Repository for working with social accounts."""

    model_type = SocialAccount
