"""
Models to store objects for offices.

All objects are either Blocks, Lines, or subclasses of those.  We use
single-table inheritance, i.e. all objects are stored in the same table
`officethings`.  This allows us to link to any kind of object from any
other (although we use polymorphism to put constraints on this).
"""
import json

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, Date, TypeDecorator

from app.db.base_class import Base


class JSONEncoded(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class FromDOMixin:
    """
    Properties to store for lining things up with DO sources.

    Not everything, of course, coemes from DO.
    """

    sourcefile = Column(String, index=True)


class OfficeThing(Base, FromDOMixin):
    """Base table for all things in offices."""

    id = Column(Integer, primary_key=True)
    discriminator = Column(String)
    # owner_id = Column(Integer, ForeignKey("user.id"))
    # owner = relationship("User", back_populates="officethings")
    rubrics = Column(String, index=True)
    posture = Column(String, index=True)
    __mapper_args__ = {
        "polymorphic_on": discriminator,
        "polymorphic_identity": "officething",
    }


class OfficeAssoc(Base):
    """Association table for references in the `officething` table."""

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("officething.id"))
    child_id = Column(Integer, ForeignKey("officething.id"))


class Block(OfficeThing, FromDOMixin):
    """Collections of objects or anything not worth representing individually."""

    __tablename__ = None

    title = Column(String, index=True)
    parts = relationship(
        "OfficeThing",
        secondary="officeassoc",
        primaryjoin="OfficeThing.id == OfficeAssoc.parent_id",
        secondaryjoin="OfficeThing.id == OfficeAssoc.child_id",
        lazy="joined",
        passive_deletes="all",
    )
    versions = Column(MutableList.as_mutable(JSONEncoded), default=[])
    __mapper_args__ = dict(polymorphic_identity="block")


class Line(OfficeThing, FromDOMixin):
    """Lines of things."""

    __tablename__ = None

    prefix = Column(String, index=True)
    suffix = Column(String, index=True)
    content = Column(String, index=True)
    __mapper_args__ = dict(polymorphic_identity="line")


class Antiphon(Line):
    """An antiphon."""

    __tablename__ = None
    __mapper_args__ = dict(polymorphic_identity="antiphon")


class Rubric(Line):
    """Lines of rubrics."""

    __tablename__ = None
    __mapper_args__ = dict(polymorphic_identity="rubric")


class HymnLine(Line):
    """Lines of hymns."""

    __mapper_args__ = dict(polymorphic_identity="hymnline")


class BibleVerse(Line):
    """A verse of the bible in some version and language."""

    @declared_attr
    def language(cls):
        """Language if not already defined."""
        return OfficeThing.__table__.c.get("language", Column(String, index=True))

    version = Column(String, index=True)
    book = Column(String, index=True)
    aka = Column(String, index=True)
    __mapper_args__ = dict(polymorphic_identity="bibleverse")


class Versicle(Block):
    """A versicle."""

    __mapper_args__ = dict(polymorphic_identity="versicle")


class Reading(Block):
    """A Reading."""

    __mapper_args__ = dict(polymorphic_identity="reading")

    ref = Column("ref", String, index=True)


class HymnVerseAssoc(Base):
    """Association table for hymn verses and lines."""

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("officething.id"))
    child_id = Column(Integer, ForeignKey("officething.id"))


class HymnAssoc(Base):
    """Association table for hymn verses and hymns."""

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("officething.id"))
    child_id = Column(Integer, ForeignKey("officething.id"))


class HymnVerse(Block):
    """Verses of hymns."""

    verseno = Column(Integer)
    parts = relationship(
        "HymnLine",
        secondary="hymnverseassoc",
        primaryjoin="OfficeThing.id == HymnVerseAssoc.parent_id",
        secondaryjoin="OfficeThing.id == HymnVerseAssoc.child_id",
        lazy="joined",
        passive_deletes="all",
    )
    # hymns = relationship(
    #     "Hymn",
    #     secondary="hymnassoc",
    #     primaryjoin="OfficeThing.id == HymnAssoc.parent_id",
    #     secondaryjoin="OfficeThing.id == HymnAssoc.child_id",
    #     lazy="joined",
    #     passive_deletes="all",
    # )


class Hymn(Block):
    """Hymns themselves."""

    parts = relationship(
        "HymnVerse",
        secondary="hymnassoc",
        primaryjoin="OfficeThing.id == HymnAssoc.parent_id",
        secondaryjoin="OfficeThing.id == HymnAssoc.child_id",
        lazy="joined",
        passive_deletes="all",
    )
    # parts = relationship(
    #     "HymnVerse",
    #     secondary="hymnassoc",
    #     primaryjoin=HymnAssoc.id == HymnAssoc.parent_id,
    #     secondaryjoin=HymnAssoc.id == HymnAssoc.child_id,
    #     lazy="joined",
    #     passive_deletes="all",
    #     collection_class=ordering_list("verseno"),
    # )
    type_ = Column(String, index=True)


class Prayer(Block):
    """A Prayer."""

    termination = relationship("Line", lazy="joined")
    termination_id = Column(Integer, ForeignKey("officething.id"))

    at = Column(MutableList.as_mutable(JSONEncoded), default=[])

    @declared_attr
    def language(cls):
        """Language column if not already present."""
        return OfficeThing.__table__.c.get("language", Column(String, index=True))

    @declared_attr
    def type_(cls):
        """Type_ column if not already present."""
        return OfficeThing.__table__.c.get("type_", Column(String, index=True))
