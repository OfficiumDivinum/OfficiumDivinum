from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class BlockMixin:
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String, index=True)
    posture = Column(String, index=True)


class FromDOMixin:
    sourcefile = Column(String, index=True)


block_line_association_table = Table(
    "block_line_association_table",
    Base.metadata,
    Column("block_id", Integer, ForeignKey("block.id"), primary_key=True),
    Column("line_id", ForeignKey("line.id"), primary_key=True),
)


class Block(Base, FromDOMixin, BlockMixin):
    """Collections of objects or anything not worth representing individually."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="blocks")
    parts = relationship(
        "Line",
        secondary=block_line_association_table,
        back_populates="blocks",
        lazy="joined",
        passive_deletes="all",
    )


class Line(Base, FromDOMixin):
    """Lines of things."""

    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(String, index=True)
    prefix = Column(String, index=True)
    suffix = Column(String, index=True)
    content = Column(String, index=True)

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="lines")
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "line"}


class Antiphon(Line):
    """
    An antiphon, for anything.

    Antiphons are just lines.
    """

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "antiphon"}


class Rubric(Line):
    """Lines of rubrics."""

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "rubric"}


class PrayerLine(Line):
    """Lines of prayers."""

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "prayerline"}
    lineno = Column(Integer)


class MartyrologyLine(Line):
    """Lines of a martyrology entry."""

    title = Column(String, index=True)
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "prayerline"}


class HymnLine(Line):
    """Lines of hymns."""

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "hymnline"}


class BibleVerse(Line):
    """A verse of the bible in some version and language."""

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "hymnline"}

    language = Column(String, index=True)
    version = Column(String, index=True)
    book = Column(String, index=True)
    aka = Column(String, index=True)
