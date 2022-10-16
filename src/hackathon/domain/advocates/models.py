from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from hackathon.lib import orm

# TODO: add Advocate links


class Advocate(orm.Base):
    """Advocate."""

    name: Mapped[str]
    short_bio: Mapped[str]
    long_bio: Mapped[str]
    years_of_experience: Mapped[int]

    __table_args__ = (
        CheckConstraint("years_of_experience >= 0", name="years_of_experience_non_negative"),
    )
