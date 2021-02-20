from typing import List, Optional

from pydantic import BaseModel

from .office_parts import BlockBase, LineBase


class MartyrologyBase(BlockBase):
    datestr: str
    title: str


class Ordinals(BaseModel):
    content: List
    language: str


class OldDateTemplate(BaseModel):
    content: str
    language: str
    ordinals: Ordinals


class MartyrologyCreate(MartyrologyBase):
    old_date_template: Optional[OldDateTemplate]


class MartyrologyUpdate(MartyrologyCreate):
    pass


# Properties shared by models stored in DB
class MartyrologyInDBBase(MartyrologyBase):
    id: int
    title: str
    old_date_template_id: int
    parts: str

    class Config:
        orm_mode = True


# Properties to return to client
class Martyrology(MartyrologyInDBBase):
    parts: List[LineBase]


# Properties properties stored in DB
class MartyrologyInDB(MartyrologyInDBBase):
    pass
