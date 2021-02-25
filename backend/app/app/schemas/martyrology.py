from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from .office_parts import BlockBase, LineBase


class Datelist(BaseModel):
    date: date


class MartyrologyBase(BlockBase):
    datestr: str
    title: str
    language: str


# Properties shared by models stored in DB
class MartyrologyInDBBase(MartyrologyBase):
    id: int = Field(gt=0)
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
class OrdinalsBase(BaseModel):
    content: List[str]
    language: str

    class Config:
        orm_mode = True


class Ordinals(OrdinalsBase):
    id: int = Field(gt=0)


class OrdinalsCreate(OrdinalsBase):
    pass


# Properties to return to client
class OldDateTemplate(BaseModel):
    content: str
    language: str
    ordinals_id: Optional[int] = Field(gt=0)
    ordinals: Optional[Ordinals]
    id: int = Field(gt=0)

    class Config:
        orm_mode = True


# Properties to accept on creation/update
class OldDateTemplateCreate(BaseModel):
    content: str
    language: str
    ordinals_id: Optional[int] = Field(gt=0)
    ordinals: Optional[OrdinalsCreate]

    # class Config:
    #     orm_mode = True


# Properties to return to client
class Martyrology(MartyrologyInDBBase):
    old_date_template: OldDateTemplate


class MartyrologyCreate(MartyrologyBase):
    old_date_template_id: Optional[int]
    julian_date: Optional[str]
    old_date_template: Optional[OldDateTemplateCreate]
    parts: Optional[List[LineBase]]


class MartyrologyUpdate(MartyrologyCreate):
    pass
