"""Parsers for all the other little bits."""
import logging
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

from .divinumofficium_structures import commands as office_names

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def extract_section_information(section_name: str, filename: str) -> Dict:
    """Extract information to name section object."""
    resp = {"qualifiers": [], "liturgical_context": [], "title": None}

    from_fn = {
        "Matutinum": ["matutinum"],
        "Major": ["laudes", "vespera"],
        "Minor": ["prima", "tertia", "sexta", "nona"],
    }
    if (match := re.search(r"(.*) Special", filename)) is not None:
        resp["liturgical_context"] += from_fn[match.groups()[0]]

    qualifier_regexs = [
        r"(Day[0-9])",
        r"(Adv)",
        r"(Quad[0-9]*)",
        r"(Pasch)",
    ]
    for regex in qualifier_regexs:
        if (match := re.search(regex, section_name)) is not None:
            resp["qualifiers"].append(match.groups()[0])
            section_name = re.sub(regex, "", section_name).strip()

    days = ["Dominica", "Feria"]
    for day in days:
        if day in section_name:
            section_name = section_name.replace(day, "").strip()
            resp["qualifiers"].append(day)

    for office in office_names:
        if office in section_name:
            office = re.search(f"({office}[0-9]*)", section_name).groups()[0]
            resp["liturgical_context"] = [office.lower()]
            candidate = section_name.replace(office, "").strip()
            section_name = candidate if candidate else section_name

    multiword_titles = ["Versum 2"]
    for title in multiword_titles:
        if title in section_name:
            resp["title"] = title.lower()
            section_name = section_name.replace(title, "").strip()

    if (match := re.search(r"(.*)M(.*)", section_name)) is not None:
        resp["version"] = "monastic"
        section_name = re.sub(r"(.*)M(.*)", r"\1\2", section_name)

    if (match := re.search(r"(Hymnus[0-9])", section_name)) is not None:
        resp["qualifiers"].append(match.groups()[0])
        section_name = re.sub(r"(.*)[0-9](.*)", r"\1\2", section_name).strip()

    if not resp["title"]:
        resp["title"] = section_name.strip().lower()
    resp = {k: v for k, v in resp.items() if v}
    logger.debug(f"Extracted {resp} from {section_name} in {filename}")
    return resp


def is_rubric(line: Line) -> Optional[str]:
    regexs = (r"^!(.*)", r"^/:(.*):/")
    for candidate in regexs:
        if (match := re.search(candidate, line.content)) is not None:
            return match.groups()[0].strip()
    return None


def parse_prayers_txt(root: Path, version: str, language: str):
    fn = root / f"{language}/Psalterium/Prayers.txt"
    sections = parse_file_as_dict(fn, version)

    matched, unmatched = magic_parser(fn, sections, language)

    logger.debug("Setting parser vars.")
    parser_vars.replacements = matched.copy()
    matched, unmatched = magic_parser(fn, sections, language)

    assert not unmatched
    return matched


def parse_file(fn: Path, version: str, language: str) -> Dict:
    sections = parse_file_as_dict(fn, version)
    matched, unmatched = magic_parser(fn, sections, language)
    assert not unmatched
    return matched


def guess_section_obj(section_name: str, section: List):
    guesses = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": [],
        "Hymnus": HymnCreate,
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
    return re.sub(r"^r\. (.)", r"::\1::", content)


def is_reference(line: Line):
    match = re.search(r"!(.*? [0-9]+:[0-9]+-[0-9]+)", line.content)
    return match if match else (re.search(r"!(In .*)", line.content))


def guess_verse_obj(verse: List, section_name):

    if re.search(r"^[VR]\.", verse[0].content):
        return VersicleCreate, {}

    if any((re.search(r"^[VR]\.", i.content) for i in verse)):
        return PrayerCreate, {}

    if len(verse) == 1:
        return LineBase, {}

    if re.search(r"^v\.", verse[0].content):
        return BlockCreate, {}

    if any((x in section_name for x in ["Lectio", "Capitulum"])):
        for candidate in (verse[0], verse[1]):
            if (match := is_reference(candidate)) is not None:
                return ReadingCreate, {"ref": match.groups()[0]}

    return [], {}

    raise UnmatchedError(f"Unable to guess type of verse {verse}")


def replace(verse: List[Line]) -> List:

    skip = [r"Dominus_vobiscum", r"Benedicamus_Domino", r".+\(.+\)"]
    sub = {"pater_noster": "Pater_noster1", "teDeum": "Te Deum"}

    new_verse = []
    for line in verse:
        if (match := re.search(r"[&$](.*)", line.content)) is not None:
            key = match.groups()[0]
            key = key.replace("~", "")
            try:
                old_key = key
                key = sub[key]
                logger.debug("Substituting {key} for {old_key}")
            except KeyError:
                pass

            if any((re.search(i, key) for i in skip)):
                logger.debug("Skipping.")
                new_verse.append(line)
                continue
            r = parser_vars.replacements[key]
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
                try:
                    verse_obj, data = guess_verse_obj(verse, section_name)
                except AttributeError as e:
                    verse_obj = []
            else:
                logger.debug("No replacements")
                raise UnmatchedError("No replacements supplied.")
        else:
            verse_obj, data = guess_verse_obj(
                [x for x in verse if type(x) not in create_types], section_name
            )

        data.update({"title": section_name, "language": language, "parts": []})

        join = False
        for line in verse:
            lineobj = None
            try:
                linenos.append(line.lineno)
            except AttributeError:  # already done.
                pass
            try:
                if is_reference(line):
                    continue
            except AttributeError:
                pass

            # don't parse twice
            if type(line) in create_types:
                data["parts"].append(line)
                lineobj = line
                continue

            if join:
                join = False
                if line.content.endswith("~"):
                    line.content = line.content[:-1]
                    join = True

                marked_up = markup(line.content)
                try:
                    data["parts"][-1].content += f" {marked_up}"
                except AttributeError:
                    data["parts"][-1].parts[-1].parts[-1].content += f" {marked_up}"
                continue
            if line.content.endswith("~"):
                line.content = line.content[:-1]
                join = True

            if line.content == "v. Orémus." and verse_obj is PrayerCreate:
                data["oremus"] = True
                continue

            if re.search(r"^[VR]\.", line.content):
                lineobj = parse_versicle(line, rubrics)
                rubrics = None
            elif (rubric := is_rubric(line)) is not None:
                rubrics = rubric
                continue
            elif " * " in line.content:
                lineobj = parse_antiphon(line)
            else:
                content = markup(strip_content(line))
                lineobj = LineBase(content=content, rubrics=rubrics, lineno=line.lineno)
                rubrics = None

            data["parts"].append(lineobj)

        if rubrics:
            data["parts"].append(RubricCreate(content=rubrics))
            if not lineobj:
                lineobj = RubricCreate(content=rubrics)

        if verse_obj is not LineBase:
            if isinstance(verse_obj, list):
                section_content.append(data["parts"])
            else:
                section_content.append(verse_obj(**data))
        elif len(section) == 1:
            section_content = lineobj

            section_content.title = section_name
        else:
            section_content.append(data["parts"])

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
            assert r
            parsed_things[section_name] = r
        except UnmatchedError as e:
            unparsed_things[section_name] = thing

    return parsed_things, unparsed_things


def parse_versicle(line, rubrics):
    match = re.search(r"([VR]\.(br.)*) (.*)", markup(line.content))
    assert match
    content = match.groups()[-1]
    prefix = match.groups()[0]
    return LineBase(content=content, prefix=prefix, lineno=line.lineno, rubrics=rubrics)


def parse_antiphon(line):
    a = AntiphonCreate(lineno=line.lineno, content=markup(line.content))
    return a


def main():
    logger.debug("In main")
    root = Path("/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/")
    version = "1960"

    parse_prayers_txt(root, version, "Latin")

    # /home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Psalterium/Revtrans.txt
    # /home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Psalterium/Matutinum Special.txt
    # /home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/SanctiM/11-17.txt
    # /home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/SanctiM/12-28.txt

    fn = Path(
        "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Psalterium/Matutinum Special.txt"
    )
    parse_file(fn, version, "Latin")

    # root = Path("/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/")
    # success = []
    # failed = []
    # errors = []
    # import typer

    # with typer.progressbar(list(root.glob("**/*.txt"))) as fns:
    #     for fn in fns:
    #         try:
    #             things = parse_file(Path(fn), version, "Latin")
    #             success.append(fn)
    #         except FileNotFoundError:
    #             pass
    #         except Exception as e:
    #             errors.append(e)
    #             failed.append(fn)

    # print(
    #     f"Parsed {(f:=len(failed)) + (s:=len(success))} files of which {s*100/(s+f) :2}% parsed"
    # )
    # for i, fn in enumerate(failed):
    #     print(fn)
    #     print(f"Errors: {errors[i]}")

    # # # parse_for_prayers(Path(fn))


if __name__ == "__main__":
    main()
