"""Dereferencer for DO links."""
import re
from pathlib import Path

from devtools import debug


def deref(linkstr: str, originf: Path):
    """Deref linkstr from original file."""
    try:
        linkstr, part = re.search(r"@(.*?):(.*):*", linkstr).groups()
        if "s/" in part:
            part = re.search(r"(.*):s/.*", part).groups()[0]
        if (match := re.search(r"(.*):[0-9]+-*[0-9]*", part)) is not None:
            part = match[1]
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
