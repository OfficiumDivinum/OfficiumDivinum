"""Utilities to handle DO's files."""
import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from devtools import debug

from app.parsers.deref import deref

logger = logging.getLogger(__name__)


class ParsingError(Exception):
    pass


class EmptyFileError(Exception):
    pass


@dataclass
class Line:
    lineno: int
    content: str


@dataclass
class Thing:
    content: Any
    crossref: Optional[str] = None
    sourcefile: str = None
    source_section: str = None


def guess_file_version(fn: Path) -> str:
    raise NotImplementedError()


def guess_section_version(section_name) -> Optional[str]:
    raise NotImplementedError()


def validate_section(section: List) -> bool:
    from app.parsers.chickenfeed import is_rubric

    if not section:
        logger.debug("Section empty.")
        return False

    flat_section = []
    for i in section:
        flat_section += i

    if all((is_rubric(x)[0] for x in flat_section)):
        logger.debug("section only rubrics.")
        return False
    else:
        return section


def parse_DO_sections(
    fn: Path, section_header_regex=r"\[(.*)\]"
) -> Dict[str, List[Union[Line, List[Line]]]]:
    """
    Parses DO files into lists per section.

    Args:
      section_header_regex:  regex to match section headers
    (Default value = r"\\[(.*)\\]")

    Returns:
      : A dict of the file, where the keys are the section headers,
      and the contents are lists.
    """

    logger.debug("Parsing section.")
    sections = {}
    current_section = None
    content = []
    subcontent = []

    lines = fn.open().readlines()
    if not lines:
        raise EmptyFileError(f"File {fn} is empty!")

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
            subcontent = [x for x in subcontent if x.content.strip()]
            if subcontent:
                content.append(subcontent)
            subcontent = []
            continue
        header = re.search(section_header_regex, line)
        if header:
            if current_section:

                subcontent = [x for x in subcontent if x.content.strip()]
                if subcontent:
                    content.append(subcontent)
                sections[current_section] = content

            current_section = header.groups()[0]
            content = []
            subcontent = []
        else:
            subcontent.append(Line(lineno, line))

    if current_section:
        subcontent = [x for x in subcontent if x.content.strip()]
        if subcontent:
            content.append(subcontent)
        if validate_section(content):
            sections[current_section] = content

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
        logger.debug("Guessed # for section header.")
        return r"#(.*)"
    else:
        logger.debug("Guessed [] for section header.")
        return r"\[(.*)\]"


def generate_commemoration_links(linkstr) -> List[str]:
    """Generates links to the *antiphons* when given a link to the *oratio* (which DO
    uses for some reason.)"""
    logger.debug("Generating commemoration links.")
    base = re.search(r"(@.*:).*", linkstr).groups()[0]
    return (f"{base}Ant 1", f"{base}Versum 1", f"{base}Ant 2", f"{base}Versum 2")


def resolve_link(targetf: Path, part: str, sublinks: bool, linkstr: str) -> List:
    """Resolve link and return linked content."""
    logger.debug(f"Resolving link to {targetf} section {part}")
    linked_content = parse_file_as_dict(
        targetf,
        part,
        sublinks,
        section_key=part,
        follow_only_interesting_links=False,
    )[part]
    linked_content = linked_content.content

    if "s/" in linkstr:
        logger.debug(f"Doing substitution for {linkstr}.")
        linked_content = substitute_linked_content(linked_content, linkstr)

    match = re.search(r":([0-9]+)-*([0-9]*)", linkstr)
    if "s/" not in linkstr and match:
        logger.debug(f"Limiting to specified lines: {linkstr}")
        start = int(match.groups()[0]) - 1
        end = match.groups()[1]
        end = int(end) if end else start + 1
        assert end > start
        linked_content = [linked_content[0][start:end]]

        assert len(linked_content[0]) == end - start

    return linked_content


def parse_file_as_dict(
    fn: Path,
    version: str = None,
    follow_links: bool = True,
    follow_only_interesting_links: bool = True,
    nasty_stuff: list = [],
    strip_keys: list = [],
    section_key: str = None,
) -> Dict:
    """
    Parses a file in DO section format and returns all sections of one kind as a dict.

    This function exists largely to take care of crossrefs.

    Args:
      fn: Path: The complete file path.
      section_key: str: The section to extract.
      version: str: We're only interested in this version (among sections).
      follow_links: bool: Whether or not to follow links.  (Default value = True)
      follow_only_interesting_links: bool: Skip links which don't change their target.
    (Default value = True)
      nasty_stuff: list:  List of regexs to squash for cleanup. (Default value = [])

    Returns:
      : A dict of sections as they are in the file, with no further processing.
    """

    section_header_regex = guess_section_header(fn)

    file_version = guess_file_version(fn)

    sections = parse_DO_sections(fn, section_header_regex)
    logger.debug(f"Got {len(sections.keys())} sections.")
    things = {}
    sourcefile = str(fn)
    for key, section in sections.items():
        section_version = guess_section_version(key)
        if section_version and section_version != version:
            continue
        version = section_version if section_version else file_version

        schemas = [r".*Special.*", r"^Minor.*"]
        if any((re.search(schema, key) for schema in schemas)):
            logger.debug(f"Skipping schema of kind {key}.")
            continue

        if section_key and not re.search(section_key, key):
            logger.debug(f"Skipping {key} as not requested key {section_key}.")
            continue

        # skip empty sections
        if not section:
            logger.debug(f"Skipping empty section.")
            continue

        flat_section = []
        for thing in section:
            flat_section += thing
        just_links = all(
            ("@" in line.content or not line.content.strip() for line in flat_section)
        )

        if just_links and follow_only_interesting_links:
            logger.debug(f"Skipping {flat_section} as only links.")
            continue

        # get DO key if it's there
        for candidate in key, section[0][0].content:
            crossref = re.search(r".*{:.-(.*):}.*", candidate)
            if crossref:
                logger.debug(f"Got DO key {crossref}.")
                crossref = crossref.groups()[0]
                break

        # if told to, remove DO's type assertions
        for k in strip_keys:
            if k in section[0][0].content:
                section[0] = section[0][1:]

        # add links to [Commemoration] sections
        if "Commemoration" in key:
            new_section = []
            for verse in section:
                linkstr = [line for line in verse if "@" in line][0]
                verse = generate_commemoration_links(linkstr) + verse  # handle later
                new_section.append(verse)
            logger.debug("Added commemoration links to antiphons.")

        for verse_index, verse in enumerate(section):
            line_index = 0
            for line in verse:
                line_index += 1

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

                # DO hand codes these, so we do too
                if (match := re.search(r"Oratio(.*) proper Gregem", part)) :
                    # proper only used for 1910
                    if version == "1910":
                        continue
                    elif version in ["DA", "1955", "1960"]:
                        logger.debug("Substituting Gregem prayer.")
                        targetf = fn.parent.parent / "Commune/C4.txt"
                        # all examples are singular, so we don't care
                        part = "Oratio9"
                    else:
                        i = match.groups()[0]
                        part = f"Oratio{i}" if i else "Oratio"

                if (match := re.search(r"Oratio(.*) Gregem", part)) :
                    if version in ["1910", "1570"]:
                        i = match.groups()[0]
                        part = f"Oratio{i}" if i else "Oratio"
                        # section[verse_index].pop(line_index)
                        # line_index -= 1
                        # continue
                    else:
                        logger.debug("Substituting Gregem prayer.")
                        targetf = fn.parent.parent / "Commune/C4.txt"
                        # all examples are singular, so we don't care
                        part = "Oratio9"

                if "Oratio proper" in part:
                    section[verse_index].pop(line_index)
                    line_index -= 1
                    continue

                logger.debug(f"Resolving for {key} {section}, {verse}")
                linked_content = resolve_link(targetf, part, sublinks, line.content)

                for extra_line in verse[line_index:]:
                    logger.debug(f"Appending line {extra_line}")
                    linked_content[-1].append(extra_line)

                if line_index > 0:
                    section[verse_index] = verse[: line_index - 1] + linked_content[0]
                else:
                    section[verse_index] = linked_content[0]

                for i, linked_verse in enumerate(linked_content[1:]):
                    section.insert(verse_index + i + 1, linked_verse)

                logger.debug(f"Final version was {section}")

                # add in anything else *after* matched section

        for i in range(len(section)):
            for j in range(len(section[i])):
                for regex in nasty_stuff:
                    section[i][j].content = re.sub(regex, "", section[i][j].content)

        things[key] = Thing(section, crossref, sourcefile, key)

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
    sub_index = 0
    for _, pattern, sub, multiline in matches:
        sub = sub.replace("$", "\\")
        sub_index += 1
        logger.debug(
            f"Doing substition {sub_index}/{len(matches)} {pattern} {sub} {multiline}"
        )

        if pattern == "^v. ":
            logger.debug("Skipping substitution of v. as we always do that.")
            continue

        new_content = []

        for linked_verse in linked_content:
            new_verse = []
            joined = None
            trash = None
            for linked_line in linked_verse:
                if joined:
                    linked_line.content = joined + " " + linked_line.content
                    joined = None

                match = re.search(pattern, linked_line.content)
                if match:
                    linked_line.content = re.sub(
                        pattern, sub, linked_line.content
                    ).strip()
                    if not linked_line.content:
                        logger.debug("Trashing emptied line.")
                        continue

                    if multiline:
                        trash = True
                        new_verse.append(linked_line)
                        break
                else:
                    logger.debug(f"Unable to match {pattern} in {linked_line.content}")
                    if linked_line.content.endswith("~"):
                        joined = linked_line.content[:-1]
                        continue

                new_verse.append(linked_line)

            new_content.append(new_verse)
            if trash:
                break

        linked_content = new_content

    return linked_content
