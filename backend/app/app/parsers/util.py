"""Utilities to handle DO's files."""
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from devtools import debug

from app.parsers.deref import deref


class ParsingError(Exception):
    pass


@dataclass
class Line:
    lineno: int
    content: str


@dataclass
class Thing:
    content: Any
    crossref: Optional[str] = None


def parse_DO_sections(
    fn: Path, section_header_regex=r"\[(.*)\]"
) -> Dict[str, List[Line]]:
    """
    Parses DO files into lists per section.

    Args:
      section_header_regex:  regex to match section headers
    (Default value = r"\\[(.*)\\]")

    Returns:
      : A dict of the file, where the keys are the section headers,
      and the contents are lists.
    """

    sections = {}
    current_section = None
    content = []
    subcontent = []

    lines = fn.open().readlines()

    skip = False

    if "@" in lines[0]:
        targetf, part = deref(lines[0], fn)
        sections = parse_DO_sections(targetf)
        skip = True

    for lineno, line in enumerate(lines):
        if skip:
            skip = False
            continue
        line = re.sub(r"\[([a-z])\]", "_\1_", line)
        line = line.strip()
        if line == "_":
            tmp_content = []
            subcontent = [x for x in subcontent if x.content.strip()]
            content.append(subcontent)
            subcontent = []
            continue
        header = re.search(section_header_regex, line)
        if header:
            if current_section:

                subcontent = [x.strip() for x in subcontent if x.strip() != ""]

                content.append(subcontent)
                if len(content) == 1:
                    content = content[0]

                sections[current_section] = content

            current_section = header.groups()[0]
            content = []
            subcontent = []
        else:
            subcontent.append(Line(lineno, line))
    return sections


def unicode_to_ascii(data: str, cleanup: bool = True):
    """
    Cleanup a unicode str.

    Modified from https://towardsdatascience.com/python-tutorial-fuzzy-name-matching-
    algorithms-7a6f43322cc5.

    Args:
      data: str: Data to asciify.
      cleanup: bool:  Whether to clean it up. (Default value = True)

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


def guess_section_header(fn: Path) -> str:
    """
    Guess the section header encoding for a given file.

    Args:
      fn: Path: The file to guess.

    Returns:
      : A regex matching the section header.
    """
    if "Ordinarium" in fn.name:
        return r"#(.*)"
    else:
        return r"\[(.*)\]"


def parse_file_as_dict(
    fn: Path,
    version: str,
    follow_links: bool = True,
    follow_only_interesting_links: bool = True,
    nasty_stuff: list = [],
) -> Dict:
    """
    Parses a file in DO section format and returns all sections of one kind as a dict.

    This function exists largely to take care of crossrefs.

    Args:
      fn: Path: The complete file path.
      section_key: str: The section to extract.
      version: str: The version in question (e.g. 1960).
      follow_links: bool: Whether or not to follow links.  (Default value = True)
      follow_only_interesting_links: bool: Skip links which don't change their target.
    (Default value = True)
      nasty_stuff: list:  List of regexs to squash for cleanup. (Default value = [])

    Returns:
      : A dict of sections as they are in the file, with no further processing.
    """
    section_header_regex = guess_section_header(fn)

    sections = parse_DO_sections(fn, section_header_regex)
    things = {}
    for key, section in sections.items():
        if "rubrica" in key:
            if version not in key:
                debug("Skipping as not for current version")
                continue

        # skip empty sections
        if not section:
            continue

        flat_section = []
        for thing in section:
            flat_section += thing
        just_links = all(("@" in line or not line.strip() for line in flat_section))

        if just_links and follow_only_interesting_links:
            continue

        # get DO key if it's there
        for candidate in key, section[0][0]:
            crossref = re.search(r".*{:.-(.*):}.*", candidate)
            if crossref:
                crossref = crossref.groups()[0]
                break

        # remove odd line telling DO the section is a section (seems to happen once)
        if re.search(f".{section_key}.*", section[0][0]):
            section[0] = section[0][1:]

        # make everything a list of lists to cope with multiline entries.
        if not isinstance(section[0], list):
            section = [section]

        for verse_index, verse in enumerate(section):
            for line_index, line in enumerate(verse):

                if not follow_links:
                    break

                if "@" not in line.content:
                    continue

                targetf, part = deref(line.content, fn)
                if not part:
                    part = key

                linked_content = None

                match = re.search(r".*s/(.*?)/(.*)/(s*)", line.content)

                if match:
                    pattern, sub, multiline = match.groups()
                else:
                    pattern = None

                sublinks = False if pattern == ".@.*" else True

                linked_content = parse_file_as_dict(targetf, part, sublinks)[part]
                linked_content = linked_content["content"]

                # make sure it's a list of verses, even if only one verse
                if not isinstance(linked_content[0], list):
                    linked_content = [linked_content]

                # assert isinstance(linked_content[0][0], Line)

                if "s/" in line.content and follow_links:
                    linked_content = substitute_linked_content(
                        linked_content, line.content
                    )

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
                for regex in nasty_stuff:
                    section[i][j] = re.sub(regex, "", section[i][j])

        things[key] = Thing(content, crossref)
    return things


def substitute_linked_content(linked_content: List, line: str) -> List[Line]:
    """
    Substitutes linked content as requested.

    Fails silently, as DO contains duplicate substitutions in places.

    Args:
      linked_content: List: linked content to substitute
      line: str: line containing substiution instructions

    Returns:
      : linked content (a list).

    Raises:
      : ParsingError: if no substitution found.
    """

    matches = re.findall(r".*?(s/(.*?)/(.*?)/(s*))", line)
    if not matches:
        raise ParsingError(f"No substitution found in {line}")
    for _, pattern, sub, multiline in matches:

        # Sometimes DO wants to strip vs.  But we already do that.
        if pattern == "^v. ":
            continue

        for linked_verse_index, linked_verse in enumerate(linked_content):
            for linked_line_index, linked_line in enumerate(linked_verse):
                match = re.search(pattern, linked_line.content)
                if match:
                    content = re.sub(pattern, sub, linked_line.content).strip()
                    if not content:
                        del linked_content[linked_verse_index][linked_line_index]
                        continue

                    lineno = linked_line.lineno
                    sub_line = Line(lineno, content)
                    linked_content[linked_verse_index][linked_line_index] = sub_line

                    if multiline:
                        # trash everything after the match
                        for i in range(linked_line_index + 1, len(linked_verse)):
                            linked_verse.pop()
                        # trash any leftover verses
                        for i in range(linked_verse_index + 1, len(linked_content)):
                            linked_content.pop()
                        break

    return linked_content
