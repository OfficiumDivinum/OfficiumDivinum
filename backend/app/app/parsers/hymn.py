"""Get all Hymns from Divinumofficium's source files."""
import re
from pathlib import Path
from typing import List, Union

from devtools import debug
from pydantic.error_wrappers import ValidationError

from app.parsers import util
from app.parsers.util import Thing
from app.schemas.hymn import HymnCreate, LineBase, VerseCreate


def guess_version(thing: Union[Path, str]):
    """
    Guess the version of a hymn from the path and filename.

    Args:
      fn: Union[Path, str]: The the filename/path or str to guess.

    Returns:
      A version str.
    """
    versions = {
        "pv": "pius v",
        "m": "monastic",
        "tr": "tridentine",
        "no": "novus ordo",
        "do": "dominican",
    }
    version = versions["pv"]

    # some files have it in the stem
    stems = {
        "1960": versions["pv"],
        "OP": versions["do"],
        "Trid": versions["tr"],
        "M": versions["m"],
        "r": versions["no"],
    }

    if isinstance(thing, str):

        for key, val in stems.items():
            if thing.split(" ")[0].endswith(key):
                return val, True

        return version, False

    else:
        for key, val in stems.items():
            if thing.stem.endswith(key):
                return val, True

        # sometimes, likewise, it's in the dirname  (only monastic atm.)
        for key, val in stems.items():
            if thing.parent.stem.endswith(key):
                return val, True

        return version, False


def parse_file(fn: Path, lang: str, calendar_version: str) -> List[HymnCreate]:
    """
    Parse a file in DO section format and return all the hymns contained.

    Args:
      fn: Path: The complete file path.
      lang: str: The lang in question (for the hymn object.)
      calendar_version: str: The calendrical version.

    Returns:
      : A list of hymn objects.  Where DO crossrefs are in the sources,
    they are stored for later use.
    """
    version, matched = guess_version(fn)

    nasty_stuff = [r".*v\. ", r".*\* *"]
    hymn_dict = util.parse_file_as_dict(
        fn,
        calendar_version,
        nasty_stuff=nasty_stuff,
        strip_keys=["#Hymnus"],
        section_key=r".*Hymnus.*",
    )
    hymns = []
    for hymn_name, section in hymn_dict.items():
        hymns.append(parse_hymn(fn, hymn_name, section, lang, version, matched))
    return hymns


def parse_hymn(
    fn: Path, hymn_name: str, section: Thing, lang: str, version: str, matched: bool
) -> HymnCreate:
    content = section.content
    crossref = section.crossref

    # create verse objects
    verses = []
    verse = []
    rubrics = None
    for thing in content:
        if verse:
            verses.append(VerseCreate(parts=verse, rubrics=rubrics))
            verse = []
            rubrics = None
        try:
            if thing[0].content.startswith("!"):
                try:
                    rubrics = thing[0].content[1:]
                except IndexError:
                    debug(thing)
                    raise Exception
        except IndexError:
            debug(content)
            raise Exception
        else:
            verse = []
            for line in thing:
                match = re.search(r"/:\((.*)\):/ (.*)", line.content)
                line_data = {"content": line.content, "lineno": line.lineno}
                if match:
                    line_data["content"] = match.groups()[1]
                    line_data["rubrics"] = match.groups()[0]
                    verse.append(LineBase(**line_data))
                else:
                    verse.append(LineBase(**line_data))
    verses.append(VerseCreate(parts=verse, rubrics=rubrics))

    # we use a regex here to strip final punctuation.
    title = re.search(r"(.*)[\.,;:]*", verses[0].parts[0].content).groups()[0]
    title = util.unicode_to_ascii(title).strip()

    if not matched:
        version, matched = guess_version(hymn_name)

    if hymn_name != "Te Deum":
        debug(hymn_name)
        if (match := re.search(".*Day([0-9]).*", hymn_name)) is not None:
            day = match.groups()[0]
            raise NotImplementedError(f"Found {day} in {fn}")
            hymn_name = re.sub("Day([0-9])", "", hymn_name).strip()
            debug(hymn_name)

        if "Special" in fn.name:
            try:
                hymn_name, season = hymn_name.split(" ")
            except ValueError:
                pass
        debug(hymn_name)
        if len(hymn_name.split(" ")) == 1:
            debug("here")
            match = re.search(r"Hymnus([0-9]*)(M*)", hymn_name)
            n, m = match.groups()
            hymn_name = "hymnus matutinum"
            hymn_name += f" {n}" if n else ""
            hymn_name += f" {m}" if m else ""
            debug(hymn_name)
        else:
            debug("name", hymn_name)
            hymn_name = " ".join(re.search(r"(Hymnus).*? ( *.*)", hymn_name).groups())
        assert hymn_name

    try:
        return HymnCreate(
            title=title,
            parts=verses,
            language=lang,
            version=version,
            crossref=crossref,
            sourcefile=fn.name,
            type_=hymn_name.lower(),
        )
    except ValidationError:
        type_ = hymn_name.lower().split(" ")
        type_ = f"{type_[0]} {type_[-1]}"
        return HymnCreate(
            title=title,
            parts=verses,
            language=lang,
            version=version,
            crossref=crossref,
            sourcefile=fn.name,
            type_=type_,
        )
