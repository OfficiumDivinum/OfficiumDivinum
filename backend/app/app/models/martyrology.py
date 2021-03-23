from functools import total_ordering
from typing import TYPE_CHECKING

import pylunar
from sqlalchemy import Boolean, Column, ForeignKey, Integer, PickleType, String, Table
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, Date, TypeDecorator

from app.db.base_class import Base

from ..DSL import dsl_parser
from .calendar import calendar_date_association_table
from .office import Block, JSONEncoded, Line, OfficeAssoc, OfficeThing

if TYPE_CHECKING:
    from .user import User  # noqa: F401


date_association_table = Table(
    "date_association_table",
    Base.metadata,
    Column("date_id", Integer, ForeignKey("datetable.id"), primary_key=True),
    Column("martyrology_id", ForeignKey("officething.id"), primary_key=True),
)


@total_ordering
class Martyrology(Block):
    """Martyrology object in database."""

    @declared_attr
    def language(cls):
        """Language if not already defined."""
        return OfficeThing.__table__.c.get("language", Column(String, index=True))

    datestr = Column(String, index=True)
    old_date_template_id = Column(Integer, ForeignKey("olddatetemplate.id"))
    old_date_template = relationship("OldDateTemplate", lazy="joined")
    julian_date = Column(String)
    old_date = None
    dates = relationship(
        "DateTable",
        secondary=date_association_table,
        back_populates="martyrologies",
        lazy="joined",
    )
    read_first = Column(Boolean)

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
            ordinals=self.old_date_template.ordinals.content,
            year=year,
            age=age,
            julian_date=self.julian_date,
        )

    def __len__(self):
        return sum(len(line.content) for line in self.parts)

    def __lt__(self, other):
        return len(self) < len(other)

    def __gt__(self, other):
        return len(self) > len(other)


class Ordinals(Base):
    """Class to represent a list of ordinals in some language or other."""

    id = Column(Integer, primary_key=True, index=True)
    content = Column(MutableList.as_mutable(JSONEncoded), default=[])
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
    ordinals = relationship("Ordinals", lazy="joined")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="old_date_templates")


class DateTable(Base):
    """Date table to resolve calendar dates into datestrs."""

    id = Column(Integer, primary_key=True, index=True)
    calendar_date = Column(Date(), index=True)
    # datestrs = Column(MutableList.as_mutable(PickleType), default=[])
    martyrologies = relationship(
        "Martyrology",
        secondary=date_association_table,
        back_populates="dates",
        lazy="joined",
    )
    feasts = relationship(
        "Feast",
        secondary=calendar_date_association_table,
        back_populates="dates",
        lazy="joined",
    )
