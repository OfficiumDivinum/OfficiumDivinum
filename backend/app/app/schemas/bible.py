from typing import Optional

from pydantic import Field

from .office_parts import LineBase


class BibleVerseBase(LineBase):
    language: str
    version: str
    book: Optional[str] = Field(None, nullable=True)
    aka: Optional[str] = Field(None, nullable=True)


class BibleVerseInDB(BibleVerseBase):
    id: int = Field(gt=0)

    class Config:
        orm_mode = True


class BibleVerse(BibleVerseInDB):
    pass


class BibleVerseCreate(BibleVerseBase):
    pass


class BibleVerseUpdate(BibleVerseInDB):
    pass
