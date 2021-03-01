from sqlalchemy import Column, ForeignKey, Integer, Table, relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, LineMixin

hymn_line_association_table = Table(
    "hymn_line_association_table",
    Base.metadata,
    Column("hymn_line_id", Integer, ForeignKey("hymnline.id"), primary_key=True),
    Column("verse_id", ForeignKey("verse.id"), primary_key=True),
)


verse_association_table = Table(
    "verse_association_table",
    Base.metadata,
    Column("verse_id", Integer, ForeignKey("verse.id"), primary_key=True),
    Column("hymn_id", ForeignKey("hymn.id"), primary_key=True),
)


class HymnLine(Base, LineMixin):
    """Lines of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_lines")
    verses = relationship(
        "Verse",
        secondary=hymn_line_association_table,
        back_populates="lines",
        lazy="joined",
    )


class Verse(Base, BlockMixin):
    """Verses of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="verses")

    lines = relationship(
        "HymnLine",
        secondary=hymn_line_association_table,
        back_populates="verses",
        lazy="joined",
    )

    hymns = relationship(
        "Hymn",
        secondary=verse_association_table,
        back_populates="verses",
        lazy="joined",
    )


class Hymn(Base, BlockMixin):
    """Hymns themselves."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymns")

    hymns = relationship(
        "Verse",
        secondary=verse_association_table,
        back_populates="hymns",
        lazy="joined",
    )
