from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    items = relationship("Item", back_populates="owner")
    ordinals = relationship("Ordinals", back_populates="owner")
    old_date_templates = relationship("OldDateTemplate", back_populates="owner")
    martyrologies = relationship("Martyrology", back_populates="owner")
    martyrology_lines = relationship("MartyrologyLine", back_populates="owner")
    verses = relationship("Verse", back_populates="owner")
    feasts = relationship("Feast", back_populates="owner")
    commemorations = relationship("Commemoration", back_populates="owner")
    hymns = relationship("Hymn", back_populates="owner")
    verses = relationship("Verse", back_populates="owner")
    hymn_lines = relationship("HymnLine", back_populates="owner")
    hymn_verses = relationship("HymnVerse", back_populates="owner")
    prayer_lines = relationship("PrayerLine", back_populates="owner")
