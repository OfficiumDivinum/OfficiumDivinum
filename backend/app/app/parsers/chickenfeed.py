"""Parsers for all the other little bits."""
import re
from pathlib import Path
from typing import Dict

from devtools import debug

from app.parsers.util import parse_file_as_dict
from app.schemas import (
    AntiphonCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    VerseCreate,
    VersicleCreate,
)


class UnmatchedError(Exception):
    pass


def get_prayers(root, version):
    fn = root / "Psalterium/Prayers.txt"
    prayers = parse_file_as_dict(fn, version)

    # uniquely, this file defines crossrefs.
    for prayer in prayers:
        prayers[prayer].crossref = prayer

    prayers = magic_parser(prayers)

    # now go back and fill in internal references like $ and &


def resolve_shorthands(thing, database):
    for line in thing:
        if line.content.startswith("$"):
            line.content = database[line.content.replace("$", "").strip()]
        if (match := re.search("&(.+)", line.content)) is not None:
            key = match.groups(0)
            line.content = re.sub("&.+", database[key])

    return thing


def guess_section_obj(section_name, section):
    guesses = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": [],
        "Lectio": ReadingCreate,
        "Responsory": VersicleCreate,
        "Hymnus": HymnCreate,
        "Capitulum": ReadingCreate,
        "Ant": AntiphonCreate,
        "Te Deum": HymnCreate,
    }
    for key, guess in guesses.items():
        if key in section_name:
            return guess

    if len(section) > 1:  # set of things. Can't be hymn as we've tested.
        return []

    section = section[0]

    if section[-1].content == "R. Amen.":
        return PrayerCreate

    if re.search(r"^[V|R]\.", section[0].content):
        return VersicleCreate

    if len(section) == 1:
        return LineBase

    raise UnmatchedError(f"Unable to guess type of section {section}")


def guess_verse_obj(section):
    if len(section) == 1:
        return None
    else:
        return VerseCreate


def magic_parser(things: Dict):
    """Magically return things as the right kind of objects."""
    parsed_linenos = []
    linenos = []
    thing = None
    things = []

    parsed_things = {}
    for section_name, section in things.items():
        section_obj = guess_section_obj(section_name)
        if type(section_obj) is type(HymnCreate):
            continue  # call hymn parser here

        rubrics = None
        section_content = []

        for line in section.content[0]:
            linenos.append(line.lineno)
            debug(line)
            parsed_lines = []
            if " * " in line.content:
                thing = parse_antiphon(line)
                parsed_linenos.append(line.lineno)

            if line.content.startswith("!"):
                rubrics = parse_rubric(line)

            if "V." in line.content or "R." in line.content:
                parsed_lines.append(parse_versicle, rubrics)
                rubrics = None

            else:
                line.rubrics = rubrics
                rubrics = None
                parsed_lines.append(line)
        if thing:
            things.append(thing)

            if type(thing) is type(last_obj):
                things.append(last_obj)
                last_obj = thing

        # wrap it all up in the right kind of object
        parsed_thing.append(parsed_lines)
        # wrap it all up again in the right kind of object

        parsed_things[key] = parsed_thing

    return parsed_things


def parse_versicle(line):
    debug(line)
    prefix, content = re.search(r"([V|R]\.) (.*)", line.content).groups()
    return LineBase(content=content, prefix=prefix, lineno=line.lineno)


def parse_rubric(line):
    return line.content.replace("!", "").strip()


def parse_antiphon(line):
    a = AntiphonCreate(lineno=line.lineno, content=line.content)
    return a


def parse_for_prayers(fn: Path):
    """Parse a given file and extract all prayers."""

    debug(fn)
    prayers_dict = parse_file_as_dict(fn, "Oratio")
    debug(prayers_dict)


# root = Path("/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/")
# version = "1960"
# get_prayers(root, version)

# fn = "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Sancti/10-02.txt"

# parse_for_prayers(Path(fn))
