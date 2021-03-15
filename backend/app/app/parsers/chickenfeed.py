"""Parsers for all the other little bits."""
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from devtools import debug

from app.DSL import days, months, ordinals, specials
from app.parsers import parser_vars, util
from app.parsers.H2obj import guess_version, parse_hymn
from app.parsers.M2obj import generate_datestr
from app.parsers.util import EmptyFileError, Line, Thing, parse_file_as_dict
from app.schemas import (
    AntiphonCreate,
    BlockCreate,
    FeastCreate,
    HymnCreate,
    LineBase,
    MartyrologyCreate,
    PrayerCreate,
    ReadingCreate,
    RubricCreate,
    VerseCreate,
    VersicleCreate,
)
from app.schemas.custom_types import versions

from .divinumofficium_structures import commands as office_names

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

create_types = (
    FeastCreate,
    MartyrologyCreate,
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


def extract_temporal_info(fn: Path) -> Optional[Dict]:
    """Extract information from temporal file."""
    data = {"qualifiers": None, "datestr": None, "name": "Feria"}

    try:
        after, day = fn.stem.split("-")
    except ValueError:
        return  # give up
    try:
        int(after)
        date = after[:-1]
        week = int(after[-1])
    except ValueError:
        date, week = re.search(r"([A-Z][a-z]+)([0-9]+)", after).groups()
    try:
        day = int(day)
    except ValueError:
        day, data["qualifiers"] = re.search(r"([0-9])(.+)", day).groups()

    try:
        date = f"1 {months[int(date) - 1]}"
    except ValueError:
        # for non month temporal it the reference *might* be a Sunday (e.g. Easter).
        date = specials[date]
    data["datestr"] = f"{ordinals[int(week)]} Sun after {date}"
    # datestr = f"{ordinals[week]} Sun on or after {date}"
    day = int(day)
    if day != 0:
        data["datestr"] = f"{days[day]} after {data['datestr']}"

    return data


def extract_section_information(section_name: str, filename: str) -> Dict:
    """Extract information to name section object."""
    resp = {"qualifiers": [], "liturgical_context": [], "title": None}

    from_fn = {
        "Matutinum": ["matutinum"],
        "Major": ["laudes", "vespera"],
        "Minor": ["prima", "tertia", "sexta", "nona"],
        "Prima": ["prima"],
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
        resp["version"] = ["monastic"]
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
    regexs = (r"^!(.*)()", r"^/:(.*):/(.*)")
    for candidate in regexs:
        if (match := re.search(candidate, line.content)) is not None:
            return [i.strip() for i in match.groups()]
    return None, None


def parse_prayers_txt(root: Path, language: str):
    fn = root / f"{language}/Psalterium/Prayers.txt"
    version = versions

    sections = parse_file_as_dict(fn, version)

    matched, unmatched = magic_parser(fn, sections, language)

    logger.debug("Setting parser vars.")
    parser_vars.replacements = matched.copy()
    matched, unmatched = magic_parser(fn, sections, language)

    assert not unmatched
    return matched


def parse_generic_file(fn: Path, version: str, language: str) -> Dict:
    sections = parse_file_as_dict(fn, version)
    matched, unmatched = magic_parser(fn, sections, language, version)
    assert not unmatched
    return matched


def parse_translations(fn: Path, language: str) -> Dict:
    section = parse_file_as_dict(fn, "")
    translations = {}
    for k, v in section.items():
        translations[k] = [LineBase(**vars(i)) for i in v.content[0]]


def guess_section_obj(section_name: str, section: List):
    guesses = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": [],
        "Hymnus": HymnCreate,
        "Ant ": AntiphonCreate,
        "Te Deum": HymnCreate,
        "Rank": FeastCreate,
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
    content = re.sub(r"^r.\ (.)", r"::\1::", content)
    content = re.sub(r" r.\ (.)", r" ::\1::", content)
    return content


def is_reference(line: Line):
    match = re.search(r"!(.*? [0-9]+:[0-9]+-[0-9]+)", line.content)
    return match if match else (re.search(r"!(In .*)", line.content))


def guess_verse_obj(verse: List, section_name):
    debug("Guessing verse obj", section_name)

    if any(("Hymnus" in section_name, "Te Deum" in section_name)):
        return VerseCreate, {}

    if re.search(r"^[VR]\.", verse[0].content):
        return VersicleCreate, {}

    if any((re.search(r"^[VR]\.", i.content) for i in verse)):
        return PrayerCreate, {}

    if any((x in section_name for x in ["Lectio", "Capitulum"])):
        debug("here")
        candidates = verse[:2]
        for candidate in candidates:
            if (match := is_reference(candidate)) is not None:
                return ReadingCreate, {"ref": match.group(1)}
        return ReadingCreate, {}

    if len(verse) == 1:
        return LineBase, {}

    if re.search(r"^v\.", verse[0].content):
        return BlockCreate, {}

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


def parse_section(
    fn: Path,
    section_name: str,
    section: Thing,
    language: str,
    version: str = None,
    section_obj=None,
):
    """Parse a section, returning the right kind of object."""

    if not section_obj:
        section_obj = guess_section_obj(section_name, section.content)
    section_data = {
        "sourcefile": section.sourcefile,
        "source_section": section.source_section,
    }
    if version:
        debug(version)
        section_data["versions"] = [version]
    section_data.update(extract_section_information(section_name, fn.name))

    if section_obj is FeastCreate:
        raise NotImplementedError("Rank section needs parsing")

    if section_obj is HymnCreate:
        hymn_version, matched = guess_version(fn)
        section_data["hymn_version"] = hymn_version
        if not matched:
            hymn_version, matched = guess_version(section_name)
            section_data["hymn_version"] = hymn_version
        assert hymn_version

    if section_obj is MartyrologyCreate:
        section_data["datestr"] = generate_datestr(section_name)
        if not section_data["datestr"]:
            logger.info(f"Skipping {section_name}")
            return None

    debug(section_obj)

    linenos = []

    rubrics = None
    section_content = []

    for verse in section.content:
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

        data.update({"language": language, "parts": []})
        if verse_obj is not VerseCreate:
            data["title"] = section_name

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

            elif is_rubric(line) != (None, None):
                rubrics, content = is_rubric(line)
                if not content:
                    continue
                line.content = content

            if not lineobj:
                if " * " in line.content and verse_obj is not VerseCreate:
                    lineobj = parse_antiphon(line)
                else:
                    content = markup(strip_content(line))
                    lineobj = LineBase(
                        content=content, rubrics=rubrics, lineno=line.lineno
                    )
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
        elif len(section.content) == 1:
            section_content = lineobj

            section_content.title = section_name
        else:
            section_content.append(data["parts"])

    if isinstance(section_content, list) and len(section_content) == 1:
        section_content = section_content[0]

    if not section_obj:
        if not isinstance(section_content, list):
            assert section_content
            section_content.sourcefile = section_data["sourcefile"]
            section_content.source_section = section_data["source_section"]
            try:
                section_content.versions = section_data["versions"]
            except (KeyError, AttributeError, ValueError):
                pass
            return section_content
        if isinstance(section_obj, list):
            debug(section_content, section_obj)
            for i in range(len(section_content)):
                try:
                    section_content[i].versions = section_data["versions"]
                    section_content[i].sourcefile = section_data["sourcefile"]
                    section_content[i].source_section = section_data["source_section"]
                except (AttributeError, ValueError, KeyError):
                    pass

        for i, verse in enumerate(section_content):
            if isinstance(verse, list):
                if len(verse) == 1:
                    section_content[i] = verse[0]
        if len(section_content) == 1:
            section_content = section_content[0]
            section_content.sourcefile = section_data["sourcefile"]
            section_content.source_section = section_data["source_section"]
            try:
                section_content.versions = section_data["versions"]
            except (KeyError, AttributeError, ValueError, KeyError):
                pass
        assert section_content
        return section_content

    else:
        if not isinstance(section_content, list):
            section_content = [section_content]
        data = {"title": section_name, "language": language, "parts": section_content}
        data.update(section_data)
        if section_obj is HymnCreate:
            debug(data)
            assert section_data["hymn_version"]
            title = re.search(
                r"(.*)[\.,;:]*", section_content[0].parts[0].content
            ).groups()[0]
            data["title"] = util.unicode_to_ascii(title).strip()
        try:
            obj = section_obj(**data)
            assert obj
            return obj
        except Exception as e:
            debug(section_obj, data)
            raise Exception(e)


def magic_parser(fn: Path, sections: Dict, language: str, version: str = None) -> Dict:
    """Magically return things as the right kind of objects."""
    parsed_things = {}
    unparsed_things = {}
    for section_name, thing in sections.items():
        if "Martyrologium" in fn.parent.name:
            section_obj = MartyrologyCreate
        else:
            section_obj = None

        try:
            r = parse_section(fn, section_name, thing, language, version, section_obj)
            if not r:
                continue
            parsed_things[section_name] = r
        except NotImplementedError:
            continue
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

    fn = Path(
        "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Martyrologium/Mobile.txt"
    )
    debug(parse_generic_file(fn, "1960", "Latin"))


if __name__ == "__main__":
    main()
