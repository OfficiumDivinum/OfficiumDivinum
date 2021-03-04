"""Utilities to handle DO's files."""
import re
import unicodedata
from pathlib import Path


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
