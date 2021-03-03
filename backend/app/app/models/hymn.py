from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, FromDOMixin, LineMixin

hymn_line_association_table = Table(
    "hymn_line_association_table",
    Base.metadata,
    Column("hymnline_id", Integer, ForeignKey("hymnline.id"), primary_key=True),
    Column("hymnverse_id", ForeignKey("hymnverse.id"), primary_key=True),
)


hymn_verse_association_table = Table(
    "hymn_verse_association_table",
    Base.metadata,
    Column("hymnverse_id", Integer, ForeignKey("hymnverse.id"), primary_key=True),
    Column("hymn_id", ForeignKey("hymn.id"), primary_key=True),
)


class HymnLine(Base, LineMixin):
    """Lines of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_lines")
    hymnverses = relationship(
        "HymnVerse",
        secondary=hymn_line_association_table,
        back_populates="parts",
        lazy="joined",
        passive_deletes="all",
    )


class HymnVerse(Base, BlockMixin):
    """HymnVerses of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_verses")
    verseno = Column(Integer)

    parts = relationship(
        "HymnLine",
        secondary=hymn_line_association_table,
        back_populates="hymnverses",
        lazy="joined",
        passive_deletes="all",
    )

    hymns = relationship(
        "Hymn",
        secondary=hymn_verse_association_table,
        back_populates="parts",
        lazy="joined",
        passive_deletes="all",
    )


class Hymn(Base, BlockMixin, FromDOMixin):
    """Hymns themselves."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymns")

    parts = relationship(
        "HymnVerse",
        secondary=hymn_verse_association_table,
        back_populates="hymns",
        lazy="joined",
        order_by="HymnVerse.verseno",
        collection_class=ordering_list("verseno"),
    )
    language = Column(String, index=True)
    crossref = Column(String, index=True)
    version = Column(String, index=True)
