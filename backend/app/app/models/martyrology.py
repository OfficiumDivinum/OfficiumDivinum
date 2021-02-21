import json
from typing import TYPE_CHECKING

import pylunar
from sqlalchemy import Column, ForeignKey, Integer, PickleType, String, types
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, TypeDecorator

from app.db.base_class import Base

from ..DSL import dsl_parser

if TYPE_CHECKING:
    from .user import User  # noqa: F401


# class Block(Base):
#     """Base class for block objects."""

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     rubrics = Column(String)
#     parts = None


class JSONEncodedDict(TypeDecorator):
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


class Martyrology(Base):
    """Martyrology object in database."""

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String)
    language = Column(String)

    datestr = Column(String, index=True)
    old_date_template_id = Column(Integer, ForeignKey("olddatetemplate.id"))
    old_date_template = relationship("OldDateTemplate")
    julian_date = Column(String)
    old_date = None
    parts = Column(MutableList.as_mutable(JSONEncodedDict), default=[])
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="martyrologies")

    def lunar(self):
        """Calculate age of moon as integer."""

        m = pylunar.MoonInfo((31, 46, 19), (35, 13, 1))  # lat/long Jerusalem
        m.update((self.date.year, self.date.month, self.date.day, 0, 0, 0))
        age = round(m.age())
        return age

    def render_old_date(self, year: int):
        """"""
        self.date = dsl_parser(self.datestr, year)
        age = self.lunar()

        from jinja2 import BaseLoader, Environment

        template = self.old_date_template.content
        template = Environment(loader=BaseLoader).from_string(template)
        self.old_date = template.render(
            ordinals=self.ordinals.content,
            year=year,
            age=age,
            julian_date=self.julian_date,
        )


class Ordinals(Base):
    """Class to represent a list of ordinals in some language or other."""

    id = Column(Integer, primary_key=True, index=True)
    content = Column(MutableList.as_mutable(PickleType), default=[])
    language = Column(String())
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="ordinals")


class OldDateTemplate(Base):
    """
    Old date template table for martyrology.

    Store jinja2 templates which recieve year, ordinals (a list) and
    age.
    """

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String())
    language = Column(String(), index=True)
    ordinals_id = Column(Integer, ForeignKey("ordinals.id"))
    ordinals = relationship("Ordinals")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="old_date_templates")
