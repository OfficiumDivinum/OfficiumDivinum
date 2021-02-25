from sqlalchemy import Column, ForeignKey, Integer, PickleType, String, Table

from app.db.base import BlockBase


class Verse(BlockBase):
    """A verse of the bible in some version and language."""

    language = Column(String)
    verse = Column(String)
