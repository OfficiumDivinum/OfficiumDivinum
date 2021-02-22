from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from .office_parts import BlockBase, LineBase


class Datelist(BaseModel):
    date: date


class MartyrologyBase(BlockBase):
    datestr: str
    title: str
    language: str


class MartyrologyCreate(MartyrologyBase):
    old_date_template_id: Optional[int]
    julian_date: Optional[str]


class MartyrologyUpdate(MartyrologyCreate):
    pass


# Properties shared by models stored in DB
class MartyrologyInDBBase(MartyrologyBase):
    id: int
    title: str
    old_date_template_id: Optional[int]
    parts: List[LineBase]
    julian_date: Optional[str]

    class Config:
        orm_mode = True


# Properties properties stored in DB
class MartyrologyInDB(MartyrologyInDBBase):
    pass


# Properties to return to client
class Ordinals(BaseModel):
    id: int
    content: List
    language: str

    class Config:
        orm_mode = True


# Properties to return to client
class OldDateTemplate(BaseModel):
    content: str
    language: str
    ordinals_id: int
    ordinals: Ordinals
    id: int

    class Config:
        orm_mode = True


# Properties to accept on creation/update
class OldDateTemplateCreate(BaseModel):
    content: str
    language: str
    ordinals_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Martyrology(MartyrologyInDBBase):
    old_date_template: OldDateTemplate
