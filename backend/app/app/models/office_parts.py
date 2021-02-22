import pylunar
from sqlalchemy import Column, ForeignKey, Integer, PickleType, String, types
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# class Item(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     owner = relationship("User", back_populates="items")


"""
Since sometimes we call parsers manually, we enforce only parsing for
calendars for which we have built Calendar() objects, otherwise we
wouldn't know what to do with the generated data.
"""
valid_calendars = [
    "1955",
    "1960",
]  # list of valid calendars. Might need an object list instead.  Or perhaps don't check and rely on in

"""Valid types of day."""
valid_day_types = ["de Tempore", "Sanctorum"]


class RankException(Exception):
    """"""


Rank = None  # temporary var to allow circular classing....


# class Line(Base):
#     """
#     Base class for renderable line objects.

#     Derived objects should set their `.template` attribute.  Be sure
#     actually to create the template (in `api/templates`) before calling
#     the method.
#     """
#     id = Column(Integer, primary_key=True, index=True)
#     prefix = Column(String, index=True)
#     suffix = Column(String, index=True)
#     rubrics = Column(String, index=True)
#     content = Column(String, index=True)
#     # do we need an owner here?


# class Link(Base):
#     """Link table."""


class Block(Base):
    """Base class for block objects."""

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String, index=True)
    parts = None


class Thing(Base):
    """Base class for things which are not blocks, i.e. don't immediately render."""

    id = Column(Integer, primary_key=True, index=True)


# class Verse(Line):
#     """Class to represent a verse of the bible."""


# class Psalm(Block):
#     parts


# class Martyrology(Block):
#     """Martyrology object."""

#     # __tablename__ = "martyrology"
#     id = Column(Integer, primary_key=True, index=True)
#     rubrics = None
#     date = relationship("Date")
#     ordinals = relationship("Ordinals")
#     old_date_template = Column(String, index=True)
#     content = Column(MutableList.as_mutable(PickleType), default=[])


# class Date(Thing):
#     """Class to represent a date."""

#     id = Column(Integer, primary_key=True, index=True)
#     rules: Column(String)
#     date: Column(types.Date)


# class Ordinals(Thing):
#     """Class to represent a list of ordinals in some language or other."""

# id = Column(Integer, primary_key=True, index=True)
# content = Column(MutableList.as_mutable(PickleType), default=[])
