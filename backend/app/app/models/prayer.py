from sqlalchemy import Column, ForeignKey, Integer, PickleType, String, Table
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, FromDOMixin, LineMixin

prayer_line_association_table = Table(
    "prayer_line_association_table",
    Base.metadata,
    Column("prayerline_id", Integer, ForeignKey("prayerline.id"), primary_key=True),
    Column("prayer_id", ForeignKey("prayer.id"), primary_key=True),
)


class PrayerLine(Base, LineMixin):
    """Lines of prayers."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="prayer_lines")
    lineno = Column(Integer)
    prayers = relationship(
        "Prayer",
        secondary=prayer_line_association_table,
        back_populates="parts",
        lazy="joined",
    )


class Prayer(Base, BlockMixin):
    """Prayers themselves."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="prayers")

    parts = relationship(
        "PrayerLine",
        secondary=prayer_line_association_table,
        back_populates="prayers",
        lazy="joined",
        order_by="PrayerLine.lineno",
        collection_class=ordering_list("lineno"),
    )
    termination = relationship("PrayerLine", lazy="joined")
    termination_id = Column(Integer, ForeignKey("prayerline.id"))
    language = Column(String, index=True)
    crossref = Column(String, index=True)
    version = Column(String, index=True)
    type_ = Column(String, index=True)
    at = Column(MutableList.as_mutable(PickleType), default=[])
