"""Parse Divinumofficium's Temporal files into Feast objects."""
from pathlib import Path
from typing import List

from devtools import debug

from app.DSL import days, months, ordinals, specials
from app.parsers.divinumofficium_structures import typo_translations
from app.schemas.calendar import FeastCreate

from .util import parse_DO_sections


def parse_rank_section(
    section: List, version: str, datestr: str, language: str, fn: Path
) -> FeastCreate:
    rank_name = "Feria"
    name, rank_name, rankno, source = [
        *section[0][0].content.split(";;"),
        None,
        None,
        None,
        None,
    ][:4]

    try:
        rank_name, octave = rank_name.split("cum")
    except ValueError:
        pass
    commemorations = None

    try:
        rank_name = typo_translations[rank_name]
    except KeyError:
        pass

    return FeastCreate(
        name=name,
        type_="de Tempore",
        datestr=datestr,
        rank_name=rank_name.lower().strip(),
        commemorations=commemorations,
        language=language,
        version=version,
        rank_defeatable=False,  # pending further information
        octave=octave,
        sourcefile=fn.name,
    )
