from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class BlockMixin:
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String, index=True)
    posture = Column(String, index=True)


class LineMixin:
    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(String, index=True)
    prefix = Column(String, index=True)
    suffix = Column(String, index=True)
    content = Column(String, index=True)


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


class Line(Base, FromDOMixin, LineMixin):
    """Collections of objects or anything not worth representing individually."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="lines")
    blocks = relationship(
        "Block",
        secondary=block_line_association_table,
        back_populates="blocks",
        lazy="joined",
        passive_deletes="all",
    )
