from sqlalchemy import Column, ForeignKey, Integer, String
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


class Block(Base, FromDOMixin, BlockMixin):
    """Collections of objects or anything not worth representing individually."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="blocks")


class Line(Base, FromDOMixin, LineMixin):
    """Collections of objects or anything not worth representing individually."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="lines")
