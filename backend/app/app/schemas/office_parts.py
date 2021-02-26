from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field


# Shared properties
class LineBase(BaseModel):
    prefix: Optional[str] = Field(None, nullable=True)
    suffix: Optional[str] = Field(None, nullable=True)
    rubrics: Optional[str] = Field(None, nullable=True)
    content: Optional[str] = Field(None, nullable=True)


class BlockBase(BaseModel):
    title: Optional[str] = Field(None, nullable=True)
    rubrics: Optional[str] = Field(None, nullable=True)
    parts: Optional[List[Union[LineBase, None]]] = Field(None, nullable=True)


class Office(BaseModel):
    officeHour: Optional[str] = Field(None, nullable=True)
    officeDate: Optional[str] = Field(None, nullable=True)
    officeClass: Optional[str] = Field(None, nullable=True)
    parts: Union[BlockBase, LineBase] = Field(None, nullable=True)


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
