from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.office_parts import FromDOMixin

from .custom_types import Datestr, RankLiteral, VersionLiteral


class CommemorationBase(BaseModel, FromDOMixin):
    """Common Commemoration properties."""

    name: str
    versions: Optional[List[VersionLiteral]]
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


class FeastBase(BaseModel, FromDOMixin):
    """Common feast properties."""

    name: str = "Feria"
    type_: str
    versions: Optional[List[VersionLiteral]]
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
