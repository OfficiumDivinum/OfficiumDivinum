"""Parse divinumofficiums martyrology files into Martyrology objects."""

import re
from pathlib import Path

from app.DSL import days, months, ordinals, specials

from .T2obj import parse_DO_sections

christ_the_king_datestr = "Sat between 23 Oct 31 Oct"


def parse_file(fn: Path):
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
        return parse_mobile_file(fn)

    month, day = (int(i) for i in fn.stem.split("-"))
    datestr = f"{day} {months[month - 1]}"
    content = []

    with fn.open() as f:
        old_date = f.readline().strip()
        f.readline()
        for line in f.readlines():
            line = line.strip()
            if not line == "_":
                content.append(line)
    return {"datestr": datestr, "julian_date": old_date, "content": content}


def parse_mobile_file(fn: Path):
    """
    Parse Martyrology 'Mobile' file.

    Parameters
    ----------
    fn: Path : mobile file to parse.


    Returns
    -------
    List of Martyrology objects with rules, which can be applied.
    """
    with fn.open() as f:
        sections = parse_DO_sections(f.readlines())

    mobile = []

    for datestr, section in sections.items():
        try:
            match = re.search(r"(.*?)([0-9]+)-([0-9])", datestr)
            special = match.group(1)
            week, day = (int(i) for i in match.group(2, 3))
            datestr = f"{ordinals[week]} {days[day]} after {specials[special]}"
        except (AttributeError, IndexError):
            if datestr == "Nativity":  # hard coded elsewhere.
                continue
            elif datestr == "10-DU":
                datestr = christ_the_king_datestr
            elif datestr == "Defuncti":  # Not sure what we need this for.
                continue
                # datestr = "2 Nov"

        mobile.append({"datestr": datestr, "content": section})
    return mobile
