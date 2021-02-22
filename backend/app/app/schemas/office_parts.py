from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel


# Shared properties
class LineBase(BaseModel):
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    rubrics: Optional[str] = None
    content: Optional[str] = None


class BlockBase(BaseModel):
    title: Optional[str] = None
    rubrics: Optional[str] = None
    parts: List[Union[LineBase, None]] = None


class Office(BaseModel):
    officeHour: Optional[str] = None
    officeDate: Optional[str] = None
    officeClass: Optional[str] = None
    parts: Union[BlockBase, LineBase] = None


# Properties to receive on item creation
class BlockCreate(BlockBase):
    pass


class LineCreate(LineBase):
    pass


# Properties to receive on item update
class BlockUpdate(BlockBase):
    pass


class LineUpdate(LineBase):
    pass


# Properties shared by models stored in DB
class BlockInDBBase(BlockBase):
    id: int

    class Config:
        orm_mode = True


class LineInDBBase(BlockBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Block(BlockInDBBase):
    pass


class Line(LineInDBBase):
    pass


# Properties properties stored in DB
class LineInDB(LineInDBBase):
    pass


class BlockInDB(BlockInDBBase):
    pass
