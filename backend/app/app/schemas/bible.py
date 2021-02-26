from typing import Optional

from pydantic import Field

from .office_parts import LineBase


class VerseBase(LineBase):
    language: str
    version: str
    book: Optional[str] = Field(None, nullable=True)
    aka: Optional[str] = Field(None, nullable=True)


class VerseInDB(VerseBase):
    id: int = Field(gt=0)

    class Config:
        orm_mode = True


class Verse(VerseInDB):
    pass


class VerseCreate(VerseBase):
    pass


class VerseUpdate(VerseInDB):
    pass
