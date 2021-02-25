from pydantic import Field

from .office_parts import BlockBase, LineBase


class ChapterBase(BlockBase):
    pass


class VerseBase(LineBase):
    language: str
    version: str
    book: str


class VerseInDB(VerseBase):
    id: int = Field(gt=0)

    class Config:
        orm_mode = True


class ChapterInDB(ChapterBase):
    id: int = Field(gt=0)

    class Config:
        orm_mode = True


class Verse(VerseInDB):
    pass


class VerseCreate(VerseInDB):
    pass


class VerseUpdate(VerseInDB):
    pass
