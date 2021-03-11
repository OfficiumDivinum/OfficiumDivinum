from typing import List, Optional

from pydantic import Field

from app.schemas.custom_types import HymnTypeLiteral, VersionLiteral
from app.schemas.office_parts import BlockBase, FromDOMixin, LineBase


class VerseBase(BlockBase):
    # type_: Optional[str] = Field(None, nullable=True)
    parts: List[LineBase]


class VerseInDB(VerseBase):
    id: int


class Verse(VerseInDB):
    pass


class VerseCreate(VerseBase):
    pass


class VerseUpdate(VerseCreate):
    pass


class HymnBase(BlockBase, FromDOMixin):
    parts: Optional[List[Verse]] = Field(None, nullable=True)
    version: str
    language: str
    type_: Optional[HymnTypeLiteral] = Field(None, nullable=True)


class HymnInDB(HymnBase):
    id: int = Field(None, nullable=True)

    class Config:
        orm_mode = True


class Hymn(HymnInDB):
    pass


class HymnCreate(HymnBase):
    parts: List[VerseCreate]
    crossref: str = Field(None, nullable=True)
    title: str


class HymnUpdate(HymnCreate):
    pass
