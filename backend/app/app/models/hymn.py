from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, LineMixin

hymn_line_association_table = Table(
    "hymn_line_association_table",
    Base.metadata,
    Column("hymn_line_id", Integer, ForeignKey("hymnline.id"), primary_key=True),
    Column("hymn_verse_id", ForeignKey("hymn_verse.id"), primary_key=True),
)


hymn_verse_association_table = Table(
    "hymn_verse_association_table",
    Base.metadata,
    Column("hymn_verse_id", Integer, ForeignKey("hymn_verse.id"), primary_key=True),
    Column("hymn_id", ForeignKey("hymn.id"), primary_key=True),
)


class HymnLine(Base, LineMixin):
    """Lines of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_lines")
    hymn_verses = relationship(
        "HymnVerse",
        secondary=hymn_line_association_table,
        back_populates="lines",
        lazy="joined",
    )


class HymnVerse(Base, BlockMixin):
    """HymnVerses of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_verses")

    parts = relationship(
        "HymnLine",
        secondary=hymn_line_association_table,
        back_populates="hymn_verses",
        lazy="joined",
    )

    hymns = relationship(
        "Hymn",
        secondary=hymn_verse_association_table,
        back_populates="parts",
        lazy="joined",
    )


class Hymn(Base, BlockMixin):
    """Hymns themselves."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymns")

    parts = relationship(
        "HymnVerse",
        secondary=hymn_verse_association_table,
        back_populates="hymns",
        lazy="joined",
    )
    version: Column(String, index=True)
    language: Column(String, index=True)
