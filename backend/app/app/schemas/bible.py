from typing import Optional

from pydantic import Field

from .office_parts import BlockBase, LineBase


class VerseBase(LineBase):
    language: str
    version: str
    book: Optional[str] = None
    aka: Optional[str] = None


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
