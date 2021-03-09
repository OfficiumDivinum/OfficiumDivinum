"""Get all Hymns from Divinumofficium's source files."""
import re
from pathlib import Path
from typing import List, Union

from devtools import debug

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
        hymns.append(parse_hymns(fn, hymn_name, section, lang, version, matched))
    return hymns


def parse_hymns(
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
                rubrics = thing[0][1:]
        except TypeError:
            debug(content)
            raise Exception
        else:
            verse = [LineBase(content=i.content) for i in thing]
    verses.append(VerseCreate(parts=verse, rubrics=rubrics))

    # we use a regex here to strip final punctuation.
    title = re.search(r"(.*)[\.,;:]*", verses[0].parts[0].content).groups()[0]
    title = util.unicode_to_ascii(title).strip()

    if not matched:
        version, matched = guess_version(hymn_name)

    hymn_name = " ".join(re.search("(Hymnus).*? ( *.*)", hymn_name).groups())
    return HymnCreate(
        title=title,
        parts=verses,
        language=lang,
        version=version,
        crossref=crossref,
        sourcefile=fn.name,
        type_=hymn_name.lower(),
    )
