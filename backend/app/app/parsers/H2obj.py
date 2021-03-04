"""Get all Hymns from Divinumofficium's source files."""
import re
from pathlib import Path
from typing import Dict, List, Union

from devtools import debug

from app.parsers import util
from app.parsers.deref import deref
from app.parsers.util import guess_section_header, parse_DO_sections, unicode_to_ascii
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


def substitute_linked_content(linked_content: List, line: str):
    """
    Substitutes linked content as requested.

    Args:
      linked_content: List: linked content to substitute
      line: str: line containing substiution instructions

    Returns:
      linked content (a list).
    """

    match = re.search(r".*s/(.*?)/(.*)/(s*)", line)
    pattern, sub, multiline = match.groups()

    # Sometimes DO wants to strip vs.  But we already do that.
    if pattern == "^v. ":
        return linked_content

    matched = False

    for linked_verse_index, linked_verse in enumerate(linked_content):
        for linked_line_index, linked_line in enumerate(linked_verse):
            match = re.search(pattern, linked_line)
            if match:
                matched = True
                linked_content[linked_verse_index][linked_line_index] = re.sub(
                    pattern, sub, linked_line
                )

                if multiline:
                    # trash everything after the match
                    for i in range(linked_line_index + 1, len(linked_verse)):
                        linked_verse.pop()
                    # trash any leftover verses
                    for i in range(linked_verse_index + 1, len(linked_content)):
                        linked_content.pop()
                    break

    assert matched
    return [
        [line.strip() for line in verse if line.strip()] for verse in linked_content
    ]


def parse_file_as_dict(fn: Path, follow_links: bool = True) -> Dict:
    """
    Parse a file in DO section format and return all the hymns contained as a dict.

    Args:
      fn: Path: The complete file path.
      follow_links: bool: Whether or not to follow links.

    Returns:
      A dict of hymn objects as they are in the file, with no further processing.
    """

    lines = fn.open().readlines()
    section_header_regex = guess_section_header(fn)

    sections = parse_DO_sections(lines, section_header_regex)
    hymns = {}
    for key, section in sections.items():
        if "Hymnus" not in key:
            continue

        # skip links
        if not section:
            continue  # something like 'Capitulum Hymnus...'

        if len(section) == 1:
            # contains only a crossref: we'll get it when we parse the original file.
            continue

        # get DO key if it's there
        for candidate in key, section[0][0]:
            crossref = re.search(r".*{:H-(.*):}.*", candidate)
            if crossref:
                crossref = crossref.groups()[0]
                break

        # remove odd line telling DO it's a hymn (seems to happen precisely once)
        if "#Hymnus" in section[0][0]:
            section[0] = section[0][1:]

        # Mostly crossrefs can be skipped.  But sometimes they
        # contain *regular expressions to generate a new hymn*.
        # Then we need to evaluate them, generate the hymn, and
        # save it under a new name.

        # make everything a list of verses
        if not isinstance(section[0], list):
            section = [section]

        for verse_index, verse in enumerate(section):
            for line_index, line in enumerate(verse):
                if not follow_links:
                    break
                if "@" not in line:
                    continue

                targetf, part = deref(line, fn)

                linked_content = None

                match = re.search(r".*s/(.*?)/(.*)/(s*)", line)
                if match:
                    pattern, sub, multiline = match.groups()
                else:
                    pattern = None
                follow_links = False if pattern == ".@.*" else True

                if "Doxolog" in line:
                    linked_lines = targetf.open().readlines()
                    linked_content = parse_DO_sections(linked_lines)[part]
                elif "Hymnus" not in line:
                    linked_content = parse_file_as_dict(targetf, follow_links)[key][
                        "content"
                    ]
                else:
                    linked_content = parse_file_as_dict(targetf, follow_links)[part][
                        "content"
                    ]

                # make sure it's a list of verses, even if only one verse
                if not isinstance(linked_content[0], list):
                    linked_content = [linked_content]

                assert linked_content

                if "s/" in line and follow_links:
                    linked_content = substitute_linked_content(linked_content, line)

                for extra_line in verse[line_index + 1 :]:
                    linked_content[-1].append(extra_line)

                if line_index > 0:
                    section[verse_index] = verse[: line_index - 1] + linked_content[0]
                else:
                    section[verse_index] = linked_content[0]

                for i, linked_verse in enumerate(linked_content[1:]):
                    section.insert(verse_index + i + 1, linked_verse)

                # add in anything else *after* matched section

        for i in range(len(section)):
            for j in range(len(section[i])):
                # remove rubbish at beginning of line
                nasty_stuff = r".*v\. "
                section[i][j] = re.sub(nasty_stuff, "", section[i][j])

                nasty_stuff = r".*\* *"
                section[i][j] = re.sub(nasty_stuff, "", section[i][j])

        hymns[key] = {"content": section, "crossref": crossref}

    return hymns


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
    version, matched = guess_version(fn)

    nasty_stuff = [r".*v\. ", r".*\* *"]
    hymn_dict = util.parse_file_as_dict(fn, "Hymnus", nasty_stuff=nasty_stuff)
    hymns = []
    for key, section in hymn_dict.items():
        content = section["content"]
        crossref = section["crossref"]

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
                if thing[0].startswith("!"):
                    rubrics = thing[0][1:]
            except TypeError:
                debug(content)
                raise Exception
            else:
                verse = [LineBase(content=i) for i in thing]
        verses.append(VerseCreate(parts=verse, rubrics=rubrics))

        # we use a regex here to strip final punctuation.
        title = re.search(r"(.*)[\.,;:]*", verses[0].parts[0].content).groups()[0]
        title = unicode_to_ascii(title).strip()

        if not matched:
            version, matched = guess_version(key)

        key = " ".join(re.search("(Hymnus).*? ( *.*)", key).groups())
        hymns.append(
            HymnCreate(
                title=title,
                parts=verses,
                language=lang,
                version=version,
                crossref=crossref,
                sourcefile=fn.name,
                type_=key.lower(),
            )
        )

    return hymns
