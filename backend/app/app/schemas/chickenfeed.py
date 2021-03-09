from typing import List

from pydantic import Field

from app.schemas.custom_types import HymnTypeLiteral
from app.schemas.office_parts import BlockBase, FromDOMixin, LineBase


class AntiphonBase(LineBase):
    pass


class AntiphonCreate(AntiphonBase):
    lineno: int = Field(None, nullable=True)
    crossref: str = Field(None, nullable=True)


class VersicleBase(BlockBase):
    parts: List[LineBase]
    lineno: int = Field(None, nullable=True)
    crossref: str = Field(None, nullable=True)


class VersicleCreate(VersicleBase):
    title: str


class ReadingBase(BlockBase):
    parts: List[LineBase]


class ReadingCreate(ReadingBase):
    pass


class RubricBase(LineBase):
    rubrics: str


class RubricCreate(RubricBase):
    pass
