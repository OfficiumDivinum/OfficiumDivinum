from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.parsers.divinumofficium_structures import (
    feria_ranks,
    new_rank_table,
    traditional_rank_lookup_table,
)

if TYPE_CHECKING:
    from .user import User  # noqa: F401


commemoration_association_table = Table(
    "commemoration_association_table",
    Base.metadata,
    Column("feast_id", Integer, ForeignKey("feast.id"), primary_key=True),
    Column("commemoration_id", ForeignKey("commemoration.id"), primary_key=True),
)


class RankMixin:
    rank_name = Column(String, index=True)
    rank_defeatable = Column(Boolean)


class Commemoration(Base, RankMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    feasts = relationship(
        "Feast",
        secondary=commemoration_association_table,
        back_populates="feasts",
        lazy="joined",
    )
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="commemorations")


class Feast(Base, RankMixin):
    """A Feast, occuring for whatever reason."""

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type_ = Column(String, index=True)
    version = Column(String, index=True)
    commemorations = relationship(
        "Commemoration",
        secondary=commemoration_association_table,
        back_populates="feasts",
        lazy="joined",
    )
    octave = Column(String, index=True)

    def _rank_to_int(self):
        """"""
        name = self.rank_name.strip().lower()
        try:
            val = traditional_rank_lookup_table[name]
        except ValueError:
            try:
                val = new_rank_table.index(name)
            except ValueError:
                return feria_ranks[name]
        return val if not self.rank_defeatable else val - 0.1
