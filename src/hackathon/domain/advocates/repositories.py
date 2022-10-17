from typing import Any

from sqlalchemy.orm import joinedload

from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

from .models import Advocate, SocialAccount


class AdvocateRepository(SQLAlchemyRepository):
    """Repository for working with Advocates data."""

    model_type = Advocate

    def before_get_execute(self, id_: Any) -> None:
        self._select = self._select.options(
            joinedload(Advocate.social_account),
            joinedload(Advocate.company),
        )


class SocialAccountRepository(SQLAlchemyRepository):
    """Repository for working with social accounts."""

    model_type = SocialAccount
