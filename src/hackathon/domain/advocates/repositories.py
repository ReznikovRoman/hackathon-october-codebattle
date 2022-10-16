from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

from .models import Advocate


class AdvocateRepository(SQLAlchemyRepository):
    """Repository for working with Advocates data."""

    model_type = Advocate
