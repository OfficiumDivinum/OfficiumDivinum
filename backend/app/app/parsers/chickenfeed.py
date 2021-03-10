"""Parsers for all the other little bits."""
import re
from pathlib import Path
from typing import Dict, List, Optional

from devtools import debug

from app.parsers import parser_vars
from app.parsers.H2obj import guess_version, parse_hymn
from app.parsers.util import Line, Thing, parse_file_as_dict
from app.schemas import (
    AntiphonCreate,
    BlockCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    RubricCreate,
    VerseCreate,
    VersicleCreate,
)

create_types = (
    AntiphonCreate,
    BlockCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    VerseCreate,
    VersicleCreate,
    RubricCreate,
)


class UnmatchedError(Exception):
    pass


def is_rubric(line: Line) -> Optional[str]:
    regexs = (r"^!(.*)", r"^/:(.*):/")
    for candidate in regexs:
        if (match := re.search(candidate, line.content)) is not None:
            return match.groups()[0].strip()
    return None


def parse_prayers_txt(root: Path, version: str, language: str):
    fn = root / f"{language}/Psalterium/Prayers.txt"
    sections = parse_file_as_dict(fn, version)

    debug(sections["Te Deum"])
    matched, unmatched = magic_parser(fn, sections, language)

    parser_vars.replacements = matched.copy()
    matched, unmatched = magic_parser(fn, sections, language)
    debug(matched["Te Deum"])
    assert matched["Te Deum"]

    assert not unmatched
    return matched


def parse_file(fn: Path, version: str, language: str) -> Dict:
    sections = parse_file_as_dict(fn, version)
    matched, unmatched = magic_parser(fn, sections, language)
    if unmatched:
        debug(unmatched)
    assert not unmatched
    return matched


def guess_section_obj(section_name: str, section: List):
    guesses = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": [],
        # "Lectio": ReadingCreate,
        # "Responsory": VersicleCreate,
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
        return VersicleCreate, {}

    if any((re.search(r"^[V|R]\.", i.content) for i in verse)):
        return PrayerCreate, {}

    if len(verse) == 1:
        return LineBase, {}

    if re.search(r"^v\.", verse[0].content):
        return BlockCreate, {}

    match = re.search(r"!(.*? [0-9]+:[0-9]+-[0-9]+)", verse[0].content)
    if match:
        return ReadingCreate, {"ref": match.groups()[0]}

    raise UnmatchedError(f"Unable to guess type of verse {verse}")


def replace(verse: List[Line]) -> List:

    skip = ["Dominus_vobiscum", "Benedicamus_Domino"]
    sub = {"pater_noster": "Pater_noster1", "teDeum": "Te Deum"}

    new_verse = []
    for line in verse:
        if (match := re.search(r"[&|$](.*)", line.content)) is not None:
            key = match.groups()[0]
            try:
                key = sub[key]
            except KeyError:
                pass
            if key in skip:
                new_verse.append(line)
                continue
            r = parser_vars.replacements[key]
            if not r:
                debug(parser_vars.replacements, key)
            assert r
            new_verse.append(r)
        else:
            new_verse.append(line)

    return new_verse


def parse_section(fn: Path, section_name: str, section: list, language: str):
    """Parse a section, returning the right kind of object."""

    section_obj = guess_section_obj(section_name, section)
    if section_obj is HymnCreate:
        version, matched = guess_version(fn)
        return parse_hymn(
            fn, section_name, Thing(content=section), language, version, matched
        )
    linenos = []

    rubrics = None
    section_content = []

    for verse in section:
        data = {}
        if all((line.content.startswith("r. ") for line in verse)):
            verse[0].content = " ".join([i.content for i in verse])
            verse = [verse[0]]

        if any((line.content.startswith("&") for line in verse)):
            if parser_vars.replacements:
                verse = replace(verse)
                verse_obj = []
            else:
                raise UnmatchedError("No replacements supplied.")
        else:
            verse_obj, data = guess_verse_obj(
                [x for x in verse if type(x) not in create_types]
            )

        data.update({"title": section_name, "language": language, "parts": []})

        join = False
        for line in verse:
            try:
                linenos.append(line.lineno)
            except AttributeError:  # already done.
                pass

            # don't parse twice
            if type(line) in create_types:
                data["parts"].append(line)
                continue

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

        if rubrics:
            data["parts"].append(RubricCreate(content=rubrics))

        if verse_obj is not LineBase:
            if isinstance(verse_obj, list):
                section_content.append(data["parts"])
            else:
                section_content.append(verse_obj(**data))
        else:
            section_content = lineobj
            section_content.title = section_name

    if isinstance(section_content, list) and len(section_content) == 1:
        section_content = section_content[0]

    if not section_obj:
        if not isinstance(section_content, list):
            assert section_content
            return section_content
        if len(section_content) == 1:
            section_content = section_content[0]
        assert section_content
        return section_content

    else:
        data = {"title": section_name, "language": language, "parts": section_content}
        debug(data, section_obj)
        try:
            obj = section_obj(**data)
            assert obj
            return obj
        except Exception as e:
            debug(section_obj, data)
            raise Exception(e)


def magic_parser(fn: Path, sections: Dict, language: str) -> Dict:
    """Magically return things as the right kind of objects."""
    parsed_things = {}
    unparsed_things = {}
    for section_name, thing in sections.items():
        try:
            r = parse_section(fn, section_name, thing.content, language)
            if not r:
                debug(thing, r)
            assert r
            parsed_things[section_name] = r
        except UnmatchedError as e:
            debug(e, thing)
            unparsed_things[section_name] = thing

    return parsed_things, unparsed_things


def parse_versicle(line, rubrics):
    prefix, content = re.search(r"([V|R]\.) (.*)", markup(line.content)).groups()
    return LineBase(content=content, prefix=prefix, lineno=line.lineno, rubrics=rubrics)


def parse_antiphon(line):
    a = AntiphonCreate(lineno=line.lineno, content=markup(line.content))
    return a


def main():
    root = Path("/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/")
    version = "1960"
    parse_prayers_txt(root, version, "Latin")

    fn = "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Sancti/10-02.txt"
    parse_file(Path(fn), version, "Latin")

    # parse_for_prayers(Path(fn))


if __name__ == "__main__":
    main()
