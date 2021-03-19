"""
Schemas to represent all parts of the office.

As usual we are vebose here.
"""

from typing import Optional

from app.schemas.office_parts import BaseModel, BlockBase

from .custom_types import nullable


class ComplineBase(BaseModel):
    incipt: Optional[BlockBase] = nullable
    lectio_brevis: Optional[BlockBase] = nullable
    psalmi: Optional[BlockBase] = nullable
    hymnus: Optional[BlockBase] = nullable
    capitulum_responsorium_versus: Optional[BlockBase] = nullable
    canticum: Optional[BlockBase] = nullable
    preces: Optional[BlockBase] = nullable
    oratio: Optional[BlockBase] = nullable
    conclusio: Optional[BlockBase] = nullable


class ComplineCreate(ComplineBase):
    incipt: Optional[BlockBase]
    lectio_brevis: Optional[BlockBase]
    psalmi: Optional[BlockBase]
    hymnus: Optional[BlockBase]
    capitulum_responsorium_versus: Optional[BlockBase]
    canticum: Optional[BlockBase]
    preces: Optional[BlockBase]
    oratio: Optional[BlockBase]
    conclusio: Optional[BlockBase]


class ComplineUpdate(ComplineCreate):
    pass


class ComplineInDB(ComplineBase):
    id: int

    class config:
        orm_mode = True


class Compline(ComplineInDB):
    pass
