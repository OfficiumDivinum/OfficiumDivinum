"""Parsers for all the other little bits."""
import re
from pathlib import Path
from typing import Dict, List, Optional

from devtools import debug

from app.parsers.H2obj import parse_hymns
from app.parsers.util import Line, parse_file_as_dict
from app.schemas import (
    AntiphonCreate,
    BlockCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    VerseCreate,
    VersicleCreate,
)


class UnmatchedError(Exception):
    pass


def is_rubric(line: Line) -> Optional[str]:
    regexs = (r"^!(.*)", r"^/:(.*):/")
    for candidate in regexs:
        if (match := re.search(candidate, line.content)) is not None:
            return match.groups()[0].strip()
    return None


def get_prayers(root: Path, version: str, language: str):
    fn = root / "Psalterium/Prayers.txt"
    prayers = parse_file_as_dict(fn, version)

    # uniquely, this file defines crossrefs.
    for prayer in prayers:
        prayers[prayer].crossref = prayer

    prayers = magic_parser(fn, prayers, language)

    # now go back and fill in internal references like $ and &


def resolve_shorthands(thing, database):
    for line in thing:
        if line.content.startswith("$"):
            line.content = database[line.content.replace("$", "").strip()]
        if (match := re.search("&(.+)", line.content)) is not None:
            key = match.groups(0)
            line.content = re.sub("&.+", database[key])

    return thing


def guess_section_obj(section_name: str, section: List):
    guesses = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": [],
        "Lectio": ReadingCreate,
        "Responsory": VersicleCreate,
        "Hymnus": HymnCreate,
        "Capitulum": ReadingCreate,
        "Ant ": AntiphonCreate,
        "Te Deum": HymnCreate,
    }
    for key, guess in guesses.items():
        if key in section_name:
            return guess

    if len(section) > 1:  # set of things. Can't be hymn as we've tested.
        return []

    return None


def strip_content(line):
    content = line.content.strip()
    if content.startswith("v. "):
        return content[3:].strip()
    else:
        return content


def markup(content: str) -> LineBase:
    return re.sub(r"r\. (.)", r"::\1::", content)


def guess_verse_obj(verse: List):

    if re.search(r"^[V|R]\.", verse[0].content):
        return VersicleCreate

    if any((re.search(r"^[V|R]\.", i.content) for i in verse)):
        return PrayerCreate

    if len(verse) == 1:
        return LineBase

    if re.search(r"^v\.", verse[0].content):
        return BlockCreate

    raise UnmatchedError(f"Unable to guess type of verse {verse}")


def parse_section(fn: Path, section_name: str, section: List, language: str):
def replace(verse: List[Line], replacements: Dict) -> List:
    new_verse = []
    for line in verse:
        if (match := re.search(r"&(.*)", line.content)) is not None:
            r = replacements[match.groups()[0]]
            new_verse.append(r)
        else:
            new_verse.append(line)

    return new_verse


    """Parse a section, returning the right kind of object."""

    section_obj = guess_section_obj(section_name, section)
    if section_obj is HymnCreate:
        return
        raise NotImplementedError("Reuse hymn parsing here.")
    linenos = []

    rubrics = None
    section_content = []

    for verse in section:

        if all((line.content.startswith("r. ") for line in verse)):
            verse = " ".join(verse)

        verse_obj = guess_verse_obj(verse)
        data = {"title": section_name, "language": language, "parts": []}
        join = False

        for line in verse:
            linenos.append(line.lineno)

            if join:
                data["parts"][-1].content += markup(line.content)
                continue

            if line.content.endswith("~"):
                join = True

            if " * " in line.content:
                lineobj = parse_antiphon(line)
            elif (rubric := is_rubric(line)) is not None:
                rubrics = rubric
                continue
            elif re.search(r"^[V|R]\.", line.content):
                lineobj = parse_versicle(line, rubrics)
                rubrics = None
            else:
                content = markup(strip_content(line))
                lineobj = LineBase(content=content, rubrics=rubrics, lineno=line.lineno)
                rubrics = None

            data["parts"].append(lineobj)

        if verse_obj is not LineBase:
            section_content.append(verse_obj(**data))
        else:
            section_content = lineobj
            section_content.title = section_name

    if not section_obj:
        if not isinstance(section_content, list):
            return section_content
        if len(section_content) == 1:
            section_content = section_content[0]
        return section_content

    else:
        data = {"title": section_name, "language": language, "parts": section_content}
        return section_obj(**data)


def magic_parser(fn: Path, sections: Dict, language: str) -> Dict:
    """Magically return things as the right kind of objects."""
    parsed_things = {}
    for section_name, thing in sections.items():
        parsed_things[section_name] = parse_section(
            fn, section_name, thing.content, language
        )

    return parsed_things


def parse_versicle(line, rubrics):
    prefix, content = re.search(r"([V|R]\.) (.*)", markup(line.content)).groups()
    return LineBase(content=content, prefix=prefix, lineno=line.lineno, rubrics=rubrics)


def parse_antiphon(line):
    a = AntiphonCreate(lineno=line.lineno, content=markup(line.content))
    return a


def parse_for_prayers(fn: Path):
    """Parse a given file and extract all prayers."""

    debug(fn)
    prayers_dict = parse_file_as_dict(fn, "Oratio")
    debug(prayers_dict)


if __name__ == "__main__":

    root = Path("/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/")
    version = "1960"
    get_prayers(root, version, "latin")

    fn = "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Sancti/10-02.txt"

    parse_for_prayers(Path(fn))
