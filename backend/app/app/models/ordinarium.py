from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base

compline_incipit_association_table = Table(
    "compline_incipit_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)


compline_lectio_brevis_association_table = Table(
    "compline_lectio_brevis_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)


compline_psalmi_association_table = Table(
    "compline_psalmi_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)

compline_hymus_association_table = Table(
    "compline_hymus_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)

compline_capitulum_responsorium_versus_association_table = Table(
    "compline_capitulum_responsorium_versus_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)

compline_canticum_association_table = Table(
    "compline_canticum_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)

compline_preces_association_table = Table(
    "compline_preces_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)

compline_oratio_association_table = Table(
    "compline_oratio_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)


compline_conclusio_association_table = Table(
    "compline_conclusio_association_table",
    Base.metadata,
    Column("compline_id", Integer, ForeignKey("compline.id"), primary_key=True),
    Column("block_id", ForeignKey("block.id"), primary_key=True),
)


class Compline(Base):
    """Ordo for compline."""

    id = Column(Integer, primary_key=True, index=True)

    incipit = relationship(
        "Block",
        secondary=compline_incipit_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    lectio_brevis = relationship(
        "Block",
        secondary=compline_lectio_brevis_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    psalmi = relationship(
        "Block",
        secondary=compline_psalmi_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    hymus = relationship(
        "Block",
        secondary=compline_hymus_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    capitulum_responsorium_versus = relationship(
        "Block",
        secondary=compline_capitulum_responsorium_versus_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    canticum = relationship(
        "Block",
        secondary=compline_canticum_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    preces = relationship(
        "Block",
        secondary=compline_preces_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    oratio = relationship(
        "Block",
        secondary=compline_oratio_association_table,
        lazy="joined",
        passive_deletes="all",
    )

    conclusio = relationship(
        "Block",
        secondary=compline_conclusio_association_table,
        lazy="joined",
        passive_deletes="all",
    )
