from typing import Literal

from pydantic import BaseModel

from app.DSL.dsl_parser import dsl_parser

RankLiteral = Literal[
    "feria",
    "commemoratio",
    "iii. classis",
    "iii. classis",
    "iii. classis",
    "ii. classis",
    "i. classis",
    "i. classis",
    "feria",
    "simplex",
    "semiduplex",
    "duplex",
    "duplex majus",
    "duplex ii classis",
    "duplex i classis",
    "duplex i classis",
    "feria minor",
    "feria major",
    "feria privilegiata",
    "feria i classis",
    "feria ii classis",
    "feria iii classis",
    "feria iv classis",
]


class Datestr(BaseModel):
    """Class to represent datestr."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate."""
        if not isinstance(v, str):
            raise TypeError("String required.")
        dsl_parser(v, 2000)

        return v

    def __repr__(self):
        return f"Datestr({super().__repr__()})"
