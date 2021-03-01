from typing import List

from pydantic import Field

from .office_parts import BlockBase, LineBase


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


class HymnBase(BlockBase):
    parts: List[Verse]
    version: str
    language: str


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
    version: str


class HymnUpdate(HymnCreate):
    pass
