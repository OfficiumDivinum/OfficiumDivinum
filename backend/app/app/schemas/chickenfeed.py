from typing import List, Optional

from pydantic import Field

from app.schemas.office_parts import BlockBase, LineBase


class AntiphonBase(LineBase):
    pass


class AntiphonCreate(AntiphonBase):
    pass


class AntiphonUpdate(AntiphonCreate):
    pass


class AntiphonInDB(AntiphonUpdate):
    id: int

    class Config:
        orm_mode = True


class Antiphon(AntiphonInDB):
    pass


class VersicleBase(BlockBase):
    parts: List[LineBase]
    lineno: int = Field(None, nullable=True)
    crossref: str = Field(None, nullable=True)


class VersicleCreate(VersicleBase):
    title: str


class VersicleUpdate(VersicleCreate):
    pass


class VersicleInDB(VersicleBase):
    id: int


class Versicle(VersicleInDB):
    pass


class ReadingBase(BlockBase):
    parts: List[LineBase]
    ref: Optional[str] = Field(None, nullable=True)


class ReadingCreate(ReadingBase):
    pass


class ReadingUpdate(ReadingCreate):
    pass


class ReadingInDB(ReadingBase):
    id: int


class Reading(ReadingInDB):
    pass


class RubricBase(LineBase):
    content: str


class RubricCreate(RubricBase):
    pass


class RubricUpdate(RubricCreate):
    pass


class RubricInDB(RubricBase):
    id: int


class Rubric(RubricInDB):
    pass
