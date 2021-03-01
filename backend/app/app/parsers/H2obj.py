"""Get all Hymns from Divinumofficium's source files."""
import re
import unicodedata
from pathlib import Path
from typing import List

from devtools import debug

from app.schemas.hymn import HymnCreate, LineBase, VerseCreate

from .T2obj import parse_DO_sections


def unicode_to_ascii(data, cleanup: bool = True):
    """
    Cleanup a unicode str.

    Modified from https://towardsdatascience.com/python-tutorial-fuzzy-name-matching-
    algorithms-7a6f43322cc5.

    Args:
      data:
      cleanup: bool:  (Default value = True)

    Returns:
    """
    if not data:
        return None
    normal = unicodedata.normalize("NFKD", data).encode("ASCII", "ignore")
    val = normal.decode("utf-8")
    if len(val.strip()) == 0:
        return data  # handle cyrillic
    if cleanup:
        val = val.lower()
        # remove special characters
        val = re.sub("[^A-Za-z0-9 ]+", " ", val)
        # remove multiple spaces
        val = re.sub(" +", " ", val)
    return val


def guess_version(fn: Path):
    """
    Guess the version of a hymn from the path and filename.

    Args:
      fn: Path: The the filename/path.

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
    }
    for key, val in stems.items():
        if fn.stem.endswith(key):
            return val

    # sometimes, likewise, it's in the dirname  (only monastic atm.)
    for key, val in stems.items():
        if fn.parent.stem.endswith(key):
            return val

    return version


def parse_file(fn: Path, lang: str) -> List[HymnCreate]:
    """
    Parse a file in DO section format and return all the hymns contained.

    Args:
      fn: Path: The complete file path.
      lang: str: The lang in question (for the hymn object.)

    Returns:
      A list of hymn objects.  Where DO crossrefs are in the sources,
      they are stored for later use.
    """
    if "Ordinarium" in str(fn):
        section_header_regex = r"#(.*)"
    else:
        section_header_regex = r"\[(.*)\]"

    debug(fn)

    version = guess_version(fn)

    lines = fn.open().readlines()

    sections = parse_DO_sections(lines, section_header_regex)
    # debug(sections)
    hymns = []
    for key, section in sections.items():
        if "Hymnus" in key:
            # skip links
            if not section:
                continue  # something like 'Capitulum Hymnus...'

            if len(section) == 1:
                continue  # contains only a crossref

            # get DO key if it's there
            try:
                crossref = re.search(r".*({.*}).*", key).groups()[0]
            except AttributeError:
                crossref = None

            debug(key, section)

            # remove rubbish at beginning of line
            nasty_stuff = r".*v. "
            section[0][0] = re.sub(nasty_stuff, "", section[0][0])

            nasty_stuff = r".*\* "
            section[-1][0] = re.sub(nasty_stuff, "", section[-1][0])

            # create verse objects
            verses = []
            verse = []
            rubrics = None
            for thing in section:
                if verse:
                    verses.append(VerseCreate(parts=verse, rubrics=rubrics))
                    verse = []
                    rubrics = None
                try:
                    if thing[0].startswith("!"):
                        rubrics = thing[0][1:]
                except TypeError:
                    print(section)
                    raise Exception
                else:
                    verse = [LineBase(content=i) for i in thing]
            verses.append(VerseCreate(parts=verse, rubrics=rubrics))
            # debug(verses)

            # debug(verses[0].parts)
            # we use a regex here to strip final punctuation.
            title = re.search(r"(.*)[\.,;:]*", verses[0].parts[0].content).groups()[0]
            title = unicode_to_ascii(title)
            hymns.append(
                HymnCreate(
                    title=title,
                    parts=verses,
                    language=lang,
                    version=version,
                    crossref=crossref,
                )
            )

    return hymns
