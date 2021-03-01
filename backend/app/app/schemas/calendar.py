from typing import List, Optional

from pydantic import BaseModel, Field

from .custom_types import Datestr, RankLiteral


class CommemorationBase(BaseModel):
    """Common Commemoration properties."""

    name: str
    version: str
    rank_name: RankLiteral
    rank_defeatable: bool


class CommemorationCreate(CommemorationBase):
    """Properties to recieve on creation."""

    datestr: Datestr


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

    name: str = "Feria"
    type_: str
    version: str
    rank_name: RankLiteral
    rank_defeatable: bool
    commemorations: Optional[List[Commemoration]]
    octave: Optional[str] = Field(None, nullable=True)
    language: str
    datestr: str


class FeastCreate(FeastBase):
    """Properties to recieve on creation."""

    commemorations: Optional[List[CommemorationCreate]]
    datestr: Datestr


class FeastInDBBase(FeastBase):
    """Feast in DB properties."""

    id: int
    owner_id: int

    class config:
        orm_mode = True


class Feast(FeastInDBBase):
    pass
