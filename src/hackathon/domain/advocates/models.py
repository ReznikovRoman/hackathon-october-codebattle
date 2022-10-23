from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackathon.lib import orm

if TYPE_CHECKING:
    from hackathon.domain.companies.models import Company


class Advocate(orm.Base):
    """Advocate."""

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("company.id"), index=True)

    name: Mapped[str]
    username: Mapped[str] = mapped_column(index=True, unique=True)
    short_bio: Mapped[str]
    long_bio: Mapped[str]
    years_of_experience: Mapped[int]
    photo_url: Mapped[str | None]

    company: Mapped["Company"] = relationship("Company", back_populates="advocates", lazy="subquery")
    social_account: Mapped["SocialAccount"] = relationship("SocialAccount", back_populates="advocate", uselist=False)

    __table_args__ = (
        CheckConstraint("years_of_experience >= 0", name="years_of_experience_non_negative"),
    )


class SocialAccount(orm.Base):
    """Advocate social account."""

    advocate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("advocate.id"), index=True, unique=True)

    github: Mapped[str | None]
    linkedin: Mapped[str | None]
    youtube: Mapped[str | None]
    twitter: Mapped[str | None]

    advocate: Mapped[Advocate] = relationship("Advocate", back_populates="social_account")
