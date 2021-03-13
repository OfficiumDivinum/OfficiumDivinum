"""Parse divinumofficiums martyrology files into Martyrology objects."""

import re
from pathlib import Path
from typing import Optional

from app.DSL import days, months, ordinals, specials
from app.schemas import LineBase, MartyrologyCreate

from .chickenfeed import parse_generic_file

christ_the_king_datestr = "Sat between 23 Oct 31 Oct"


def parse_file(fn: Path, lang: str, title: str):
    """
    Parse Martyrology file.

    Parameters
    ----------
    fn: Path : file to parse.


    Returns
    -------
    Martyrology object with rule for specific day.
    """
    if fn.stem == "Mobile":
        return parse_generic_file(fn)

    month, day = (int(i) for i in fn.stem.split("-"))
    datestr = f"{day} {months[month - 1]}"
    content = []

    # print("File:", fn)

    with fn.open() as f:
        julian_date = f.readline().strip()
        f.readline()
        for line in f.readlines():
            line = line.strip()
            if not line == "_":
                content.append(LineBase(content=line))

    return MartyrologyCreate(
        parts=content,
        datestr=datestr,
        julian_date=julian_date,
        language=lang,
        title=title,
        sourcefile=fn.name,
    )


def generate_datestr(section_name: str) -> Optional[str]:
    try:
        match = re.search(r"(.*?)([0-9]+)-([0-9])", section_name)
        special = match.group(1)
        week, day = (int(i) for i in match.group(2, 3))
        return f"{ordinals[week]} {days[day]} after {specials[special]}"
    except (AttributeError, IndexError):
        if section_name == "Nativity":  # hard coded elsewhere.
            return None
        elif section_name == "10-DU":
            return christ_the_king_datestr
        elif "Defuncti" in section_name:  # Not sure what we need this for.
            return None
