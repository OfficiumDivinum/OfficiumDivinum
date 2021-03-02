"""Utilities to handle DO's files."""
import re


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
