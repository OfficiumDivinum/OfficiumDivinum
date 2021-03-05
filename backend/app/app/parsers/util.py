"""Utilities to handle DO's files."""
import re
import unicodedata
from pathlib import Path
from typing import Dict, List

from devtools import debug

from app.parsers.deref import deref


def parse_DO_sections(lines: list, section_header_regex=r"\[(.*)\]") -> list:
    """
    Parses DO files into lists per section.

    Args:
      lines: list : lines to break into sections.

    Returns:
      A dict of the file, where the keys are the section headers,
      and the contents are lists.
    """

    sections = {}
    current_section = None
    content = []
    subcontent = []
    for line in lines:
        line = re.sub(r"\[([a-z])\]", "_\1_", line)
        line = line.strip()
        if line == "_":
            subcontent = [x.strip() for x in subcontent if x.strip() != ""]
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
            subcontent.append(line)
    return sections


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


def guess_section_header(fn: Path):
    if "Ordinarium" in fn.name:
        return r"#(.*)"
    else:
        return r"\[(.*)\]"


def parse_file_as_dict(
    fn: Path,
    section_key: str,
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
      follow_links: bool: Whether or not to follow links.  (Default value = True)
      follow_only_interesting_links: bool: Skip links which don't change their target.
    (Default value = True)
      nasty_stuff: list:  List of regexs to squash for cleanup. (Default value = [])

    Returns:
      : A dict of sections as they are in the file, with no further processing.
    """

    lines = fn.open().readlines()
    section_header_regex = guess_section_header(fn)

    sections = parse_DO_sections(lines, section_header_regex)
    hymns = {}
    for key, section in sections.items():
        if section_key not in key:
            continue

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

        # parse crossrefs

        # make everything a list of lists to cope with multiline entries.

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

                sublinks = False if pattern == ".@.*" else True

                debug(part)  # need to find a programmatic way of getting it

                if section_key in line:
                    target_key = section_key
                else:
                    target_key = section_key
                    part = key

                linked_content = parse_file_as_dict(targetf, target_key, sublinks)[part]
                linked_content = linked_content["content"]

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
                for regex in nasty_stuff:
                    section[i][j] = re.sub(regex, "", section[i][j])

        hymns[key] = {"content": section, "crossref": crossref}

    return hymns


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
