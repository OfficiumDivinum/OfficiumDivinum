from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, FromDOMixin, LineMixin


class Antiphon(Base, LineMixin, FromDOMixin):
    """
    An antiphon, for anything.

    Antiphons are just lines.
    """

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="antiphons")


versicle_line_association_table = Table(
    "versicle_line_association_table",
    Base.metadata,
    Column("versicle_id", Integer, ForeignKey("versicle.id"), primary_key=True),
    Column("line_id", ForeignKey("line.id"), primary_key=True),
)

reading_line_association_table = Table(
    "reading_line_association_table",
    Base.metadata,
    Column("reading_id", Integer, ForeignKey("reading.id"), primary_key=True),
    Column("line_id", ForeignKey("line.id"), primary_key=True),
)


class Versicle(Base, BlockMixin, FromDOMixin):
    """A versicle."""

    parts = relationship(
        "Line",
        secondary=versicle_line_association_table,
        back_populates="blocks",
        lazy="joined",
        passive_deletes="all",
    )
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="versicles")


class Reading(Base, BlockMixin, FromDOMixin):
    """A Reading."""

    ref = Column("ref", String, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="readings")
    parts = relationship(
        "Line",
        secondary=reading_line_association_table,
        back_populates="blocks",
        lazy="joined",
        passive_deletes="all",
    )


class Rubric(Base, LineMixin, FromDOMixin):
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="rubrics")
