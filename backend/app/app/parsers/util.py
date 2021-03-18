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
# logging.basicConfig(level=logging.DEBUG)


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


rubrica_versions = {
    "1960": ["1960"],
    "1955": ["1955"],
    "DA": ["divino"],
    "1910": ["1910", "tridentina"],
    "1570": ["1570", "tridentina"],
    "newcal": ["innovata"],
    "monastic": ["monastica"],
}


def resolve_rubrica_header(line: str, version: str) -> bool:
    """Resolve rubrica in header."""
    try:
        versions = rubrica_versions[version]
    except (KeyError, TypeError):
        return True

    if (match := re.search(r"(\(rubrica.*\))", line)) :
        if any((x in match.group(1) for x in versions)):
            return True
        else:
            return False
    else:
        return True


def resolve_rubrica(line: str, version: str) -> Dict:
    """
    Resolve rubrica.

    Args:
      line: str: line to resolve.
      version: str: version to resolve against.
    """
    line = line.strip()
    data = {
        "line": None if "rubrica" in line else line,
        "replace_previous": False,
        "skip_next": False,
    }
    try:
        versions = rubrica_versions[version]
    except (TypeError, KeyError):
        data["line"] = line
        return data

    if (match := re.search(r"(.+)(\(.*rubrica.*\))", line)) :
        if any((x in match.group(2) for x in versions)):
            data["line"] = match.group(1).strip()

    elif (match := re.search(r"(\(.*rubrica.*\)(.+))", line)) :
        if any((x in match.group(1) for x in versions)):
            data["line"] = match.group(2).strip()

    elif (match := re.search(r"^\(.*?rubrica (.*)dicuntur\)$", line.strip())) :
        if any((x in match.group(1) for x in versions)):
            data["replace_previous"] = True
        else:
            data["skip_next"] = True

    elif (match := re.search(r"^\(.*rubrica (.*)omittitur\)$", line.strip())) :
        if any((x in match.group(1) for x in versions)):
            data["replace_previous"] = True

    elif (match := re.search(r"^\(.*rubrica (.*)\)$", line.strip())) :
        if not any((x in match.group(1) for x in versions)):
            data["skip_next"] = True

    return data


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
    fn: Path, section_header_regex=r"\[(.*)\]", version=None
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
        try:
            data = resolve_rubrica(lines[1], version)
        except IndexError:
            data = {"replace_previous": False}

        if not data["replace_previous"]:
            targetf, part = deref(lines[0], fn)
            sections = parse_DO_sections(targetf)
            skip = True
        else:
            lines = lines[2:]

    old_header = None
    for lineno, line in enumerate(lines):
        if skip:
            skip = False
            continue
        line = line.strip()
        if not line:
            continue

        # rubrica
        header = re.search(section_header_regex, line)
        if not header:
            data = resolve_rubrica(line, version)
            if data["replace_previous"]:
                subcontent.pop()
            if data["skip_next"]:
                skip = True
            line = data["line"]
            if not line:
                continue

        line = re.sub(r"\[([a-z])\]", "_\1_", line)
        line = line.strip()
        if line == "_":
            subcontent = [x for x in subcontent if x.content.strip()]
            if subcontent:
                content.append(subcontent)
            subcontent = []
            continue
        if header:
            if current_section:

                subcontent = [x for x in subcontent if x.content.strip()]
                if subcontent:
                    content.append(subcontent)
                if resolve_rubrica_header(old_header, version):
                    sections[current_section] = content

            current_section = header.group(1)
            old_header = line
            content = []
            subcontent = []
        else:
            subcontent.append(Line(lineno, line))

    if current_section:
        if resolve_rubrica_header(old_header, version):
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
    base = re.search(r"(@.*:).*", linkstr).group(1)
    return (f"{base}Ant 1", f"{base}Versum 1", f"{base}Ant 2", f"{base}Versum 2")


def resolve_link(
    targetf: Path, part: str, sublinks: bool, linkstr: str, version: str
) -> List:
    """Resolve link and return linked content."""
    logger.debug(f"Resolving link to {targetf} section {part}")

    linked_content = parse_file_as_dict(
        targetf,
        version,
        follow_links=sublinks,
        section_key=part,
        follow_only_interesting_links=False,
    )[part]
    linked_content = linked_content.content
    assert all(x for x in linked_content)
    debug(linked_content)

    verses = []
    for verse in linked_content:
        v = []
        for line in verse:
            if "&TeDeum" not in line.content:
                v.append(line)
        verses.append(v)

    linked_content = verses
    assert all(x[0] for x in linked_content)

    if "s/" in linkstr:
        logger.debug(f"Doing substitution for {linkstr}.")
        linked_content = substitute_linked_content(linked_content, linkstr)

    match = re.search(r":([0-9]+)-*([0-9]*)", linkstr)
    if "s/" not in linkstr and match:
        logger.debug(f"Limiting to specified lines: {linkstr}")
        start = int(match.group(1)) - 1
        end = match.groups()[1]
        end = int(end) if end else start + 1
        assert end > start

        # turn it back into a flat list, then split again
        # this whole pattern is wrong: we should work on lists of lines, like DO does, and split later.
        flat = []
        for verse in linked_content:
            flat += verse
            flat.append("_")
        flat = flat[start:end]
        linked_content = []
        verse = []
        for line in flat:
            if line == "_":
                if verse:
                    linked_content.append(verse)
                verse = []
                continue
            else:
                verse.append(line)
        if verse:
            linked_content.append(verse)

    # assert linked_content, f"Link was empty {linked_content}, {linkstr}"
    # assert linked_content[0], f"{linked_content}"

    return linked_content


def parse_file_as_dict(
    fn: Path,
    version: str,
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
    sections = parse_DO_sections(fn, section_header_regex, version)

    logger.debug(f"Got {len(sections.keys())} sections.")
    things = {}
    sourcefile = str(fn)
    for key, section in sections.items():

        schemas = [r".*Special.*", r"^Minor.*"]
        if any((re.search(schema, key) for schema in schemas)):
            logger.debug(f"Skipping schema of kind {key}.")
            continue

        if section_key and not re.search(section_key, key):
            logger.debug(f"Skipping {key} as not requested key {section_key}.")
            continue

        # skip empty sections
        if not section:
            logger.debug(f"Skipping empty section. {section}, {key}")
            continue

        flat_section = []
        for thing in section:
            flat_section += thing

        just_links = all(
            (
                ("@" in line.content and "s/" not in line.content)
                or not line.content.strip()
                for line in flat_section
            )
        )

        if just_links and follow_only_interesting_links:
            logger.debug(f"Skipping {flat_section} ({key}) as only links.")
            continue

        # get DO key if it's there
        for candidate in key, section[0][0].content:
            crossref = re.search(r".*{:.-(.*):}.*", candidate)
            if crossref:
                logger.debug(f"Got DO key {crossref}.")
                crossref = crossref.group(1)
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

        restart = False
        while follow_links:
            new_section = []

            for verse_index, verse in enumerate(section):
                new_verse = []
                for line_index, line in enumerate(verse):
                    if "@" not in line.content:
                        new_verse.append(line)
                        continue

                    linked_content = None
                    targetf, part = deref(line.content, fn)
                    if not part:
                        part = key
                    match = re.search(r".*s/(.*?)/(.*)/(s*)", line.content)
                    if match:
                        pattern, sub, multiline = match.groups()

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
                            i = match.group(1)
                            part = f"Oratio{i}" if i else "Oratio"

                    if (match := re.search(r"Oratio(.*) Gregem", part)) :
                        if version in ["1910", "1570"]:
                            i = match.group(1)
                            part = f"Oratio{i}" if i else "Oratio"
                        else:
                            logger.debug("Substituting Gregem prayer.")
                            targetf = fn.parent.parent / "Commune/C4.txt"
                            # all examples are singular, so we don't care
                            part = "Oratio9"

                    if "Oratio proper" in part:
                        continue

                    logger.debug(
                        f"Resolving for {key}, section: {section}, verse: {section[verse_index]}, line: {line}"
                    )
                    sublinks = False if (targetf == fn) else True
                    linked_content = resolve_link(
                        targetf, part, sublinks, line.content, version
                    )
                    assert (
                        linked_content
                    ), f"Section was empty: {section}, {linked_content} {line.content}"
                    assert linked_content[
                        0
                    ], f"Section[0] was empty: {section}, ({linked_content}) {line.content}"

                    if not linked_content[0]:
                        logger.debug(
                            f"Link {line.content} was link to nothing, skipping"
                        )
                        continue
                    logger.debug(f"Got {linked_content} for {key}.")

                    # append linked verse at point
                    new_verse += linked_content[0]
                    # append rest of verse if any.
                    new_verse += verse[line_index + 1 :]

                    new_section.append(new_verse)
                    new_section += linked_content[1:]
                    new_section += section[verse_index + 1 :]
                    restart = True
                    break

                if not restart:
                    new_section.append(new_verse)

            section = new_section
            if not restart:
                break
            else:
                restart = False

        assert section, "Section somehow empty!"
        assert section[0], f"Section v1. empty! {section}"

        for i in range(len(section)):
            for j in range(len(section[i])):
                for regex in nasty_stuff:
                    section[i][j].content = re.sub(regex, "", section[i][j].content)

        things[key] = Thing(section, crossref, sourcefile, key)

    return things


def substitute_linked_content(linked_content: List, linkstr: str) -> List[Line]:
    """
    Substitutes linked content as requested.

    Fails silently, as DO contains duplicate substitutions in places.

    Args:
      linked_content: List: linked content to substitute
      linkstr: str: line containing substiution instructions

    Returns:
      : linked content (a list).

    Raises:
      : ParsingError: if no substitution found.
    """
    assert linked_content[0]
    offset = linked_content[0][0].lineno
    verses = []
    for verse in linked_content:
        verses.append("\n".join(x.content for x in verse))
    one_line = "\n_\n".join(verses)

    matches = re.findall(r".*?(s/(.*?)/(.*?)/(s*m*g*))", linkstr)
    if not matches:
        raise ParsingError(f"No substitution found in {linkstr}")

    sub_index = 0
    for _, pattern, sub, multiline in matches:
        if "g" in multiline:
            count = 0
        else:
            count = 1

        flags = 0
        if "m" in multiline:
            flags = re.MULTILINE
        if "s" in multiline:
            flags += re.S

        sub = sub.replace("$", "\\")
        sub_index += 1
        logger.debug(
            f"Doing substition {sub_index}/{len(matches)} {pattern} {sub} {multiline}"
        )
        one_line = re.sub(pattern, sub, one_line, count, flags=flags)

    verses = []
    for verse in one_line.split("_"):
        v = []
        for i, line in enumerate(verse.split("\n")):
            line = Line(i + offset, line.strip())
            if line.content:
                v.append(line)
        if v:
            verses.append(v)

    assert all(x[0] for x in verses), f"{verses}"
    return verses
