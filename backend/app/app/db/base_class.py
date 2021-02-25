from typing import Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


@as_declarative()
class BlockBase:
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String, index=True)
    parts = None
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
