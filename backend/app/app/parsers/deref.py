"""Dereferencer for DO links."""
import re
from pathlib import Path

from devtools import debug


def deref(linkstr: str, originf: Path):
    """
    Deref linkstr from original file.

    Args:
      linkstr: str: String containing DO link content.
      originf: Path: Path to original file to resolve against.

    Returns:
      targetf: Path: Path to target file
      part: str: Part to extract
    """
    try:
        linkstr, part = re.search(r"@(.*?):(.*):*", linkstr).groups()
        if "s/" in part:
            part = re.search(r"(.*?):s/.*", part).group(1)
        if (match := re.search(r"(.*):[0-9]+-*[0-9]*", part)) is not None:
            part = match.group(1)
        part = re.sub("(.*):$", r"\1", part)
    except AttributeError:
        linkstr = linkstr.replace("@", "").strip()
        part = None
    if not linkstr:
        targetf = originf
    if "/" in linkstr:
        targetf = originf.parent.parent / f"{linkstr}.txt"
    else:
        targetf = originf

    return targetf, part
