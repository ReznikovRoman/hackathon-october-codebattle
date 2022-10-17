from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackathon.lib import orm

if TYPE_CHECKING:
    from hackathon.domain.advocates.models import Advocate


class Company(orm.Base):
    """Company."""

    name: Mapped[str] = mapped_column(index=True, unique=True)
    summary: Mapped[str]

    advocates: Mapped[list["Advocate"]] = relationship("Advocate", back_populates="company", lazy="subquery")
