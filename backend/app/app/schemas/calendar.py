from typing import List, Optional

from pydantic import BaseModel


class CommemorationBase(BaseModel):
    """Common Commemoration properties."""

    name: str
    version: str
    rank_name: str
    rank_defeatable: bool


class CommemorationCreate(CommemorationBase):
    """Properties to recieve on creation."""


class CommemorationInDBBase(CommemorationBase):
    """Commemoration in DB properties."""

    id: int
    owner_id: int

    class config:
        orm_mode = True


class Commemoration(CommemorationInDBBase):
    """Properties to return to client."""


class FeastBase(BaseModel):
    """Common feast properties."""

    name: str
    type_: str
    version: str
    rank_name: str
    rank_defeatable: bool
    commemorations: Optional[List[Commemoration]]
    octave: str


class FeastCreate(FeastBase):
    """Properties to recieve on creation."""

    commemorations: Optional[List[CommemorationCreate]]


class FeastInDBBase(FeastBase):
    """Feast in DB properties."""

    id: int
    owner_id: int

    class config:
        orm_mode = True


class Feast(FeastInDBBase):
    pass
