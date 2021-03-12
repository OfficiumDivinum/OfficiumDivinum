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
    "semiduplex i classis",
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

OfficeLiteral = Literal[
    "laudes",
    "matutinum",
    "prima",
    "tertia",
    "sexta",
    "nona",
    "versperas",
    "completorium",
]

HymnTypeLiteral = Literal[
    "hymnus minor",
    "hymnus vespera",
    "hymnus matutinum",
    "hymnus matutinum 1",
    "hymnus laudes",
    "hymnus prima",
    "hymnus tertia",
    "hymnus sexta",
    "hymnus nona",
    "hymnus vespera 3",
    "te deum",
    "hymnus laudes2",
]

VersionLiteral = Literal["Monastic", "1570", "1910", "DA", "1955", "1960", "OP"]

PrayerTypeLiteral = Literal["Oratio"]


class Datestr(BaseModel):
    """Class to represent datestr."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        """Update schema so we have some idea how to generate this stuff."""
        field_schema.update(
            examples=[
                "Easter",
                "1 Jan",
                "Sun after 2 Jan LEAPYEAR OR 16 Jan NOTLEAPYEAR",
                "Sun between 2 Jan 4 Jan OR 2 Jan",
            ]
        )

    @classmethod
    def validate(cls, v):
        """Validate."""
        if not isinstance(v, str):
            raise TypeError("String required.")
        dsl_parser(v, 2000)

        return v

    def __repr__(self):
        return f"Datestr({super().__repr__()})"
