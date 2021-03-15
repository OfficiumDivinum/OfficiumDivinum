from typing import List, Optional

from pydantic import Field

from app.schemas.custom_types import HymnTypeLiteral
from app.schemas.office_parts import BlockBase, LineBase


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
    ref: Optional[str] = Field(None, nullable=True)


class ReadingCreate(ReadingBase):
    pass


class RubricBase(LineBase):
    content: str


class RubricCreate(RubricBase):
    pass
