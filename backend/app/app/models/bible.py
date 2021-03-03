from sqlalchemy import Column, ForeignKey, Integer, PickleType, String, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.office_parts import FromDOMixin, LineMixin


class Verse(Base, LineMixin, FromDOMixin):
    """A verse of the bible in some version and language."""

    language = Column(String, index=True)
    version = Column(String, index=True)
    book = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="verses")
    aka = Column(String, index=True)

    # chapters = relationship(
    #     "Chapter",
    #     secondary=line_association_table,
    #     back_populates="parts",
    #     lazy="joined",
    # )


# class Chapter(BlockBase):
#     """A chapter of the bible."""
#     parts = relationship(
#         "Verse",
#         secondary=line_association_table,
#         back_populates="chapters",
#         lazy="joined",
#     )
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     owner = relationship("User", back_populates="martyrologies")
