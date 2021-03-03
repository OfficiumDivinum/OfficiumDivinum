from typing import Optional

from pydantic import Field

from app.schemas.office_parts import FromDOMixin

from .office_parts import LineBase


class VerseBase(LineBase, FromDOMixin):
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
