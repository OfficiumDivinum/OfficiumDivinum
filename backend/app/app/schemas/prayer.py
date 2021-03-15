from typing import List, Optional

from pydantic import Field

from app.schemas.custom_types import PrayerTypeLiteral, VersionLiteral
from app.schemas.office_parts import BlockBase, LineBase


class PrayerBase(
    BlockBase,
):
    parts: List[LineBase]
    termination: Optional[LineBase] = Field(None, nullable=True)
    version: Optional[VersionLiteral]
    language: str
    type_: Optional[PrayerTypeLiteral] = Field(None, nullable=True)


class PrayerInDB(PrayerBase):
    id: int = Field(None, nullable=True)

    class Config:
        orm_mode = True


class Prayer(PrayerInDB):
    pass


class PrayerCreate(PrayerBase):
    parts: List[LineBase]
    termination_id: Optional[int] = Field(None, nullable=True)
    crossref: str = Field(None, nullable=True)
    title: Optional[str] = Field(None, nullable=True)
    version: Optional[VersionLiteral] = Field(None, nullable=True)
    oremus: bool = Field(None, nullable=True)


class PrayerUpdate(PrayerCreate):
    pass
