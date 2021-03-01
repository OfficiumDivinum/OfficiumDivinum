"""Get all Hymns from Divinumofficium's source files."""
import re
import unicodedata
from pathlib import Path
from typing import List

from devtools import debug

from app.schemas.hymn import HymnCreate, LineBase, VerseCreate

from .T2obj import parse_DO_sections


def unicode_to_ascii(data, cleanup: bool = True):
    """Pulled from https://towardsdatascience.com/python-tutorial-fuzzy-name-matching-
    algorithms-7a6f43322cc5."""
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


def parse_file(fn: Path, lang: str, version: str) -> List[HymnCreate]:
    if "Ordinarium" in str(fn):
        section_header_regex = r"#(.*)"
    else:
        section_header_regex = r"\[(.*)\]"

    lines = fn.open().readlines()

    sections = parse_DO_sections(lines, section_header_regex)
    hymns = []
    for key, section in sections.items():
        if "Hymnus" in key:
            # skip links
            if not section:
                continue  # something like 'Capitulum Hymnus...'

            if len(section) == 1:
                continue

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
            title = re.search(r"(.*)[\.,;:]*", verses[0].parts[0].content).groups()[0]
            title = unicode_to_ascii(title)
            hymns.append(
                HymnCreate(title=title, parts=verses, language=lang, version=version)
            )

    return hymns
