"""Dereferencer for DO links."""
import re
from pathlib import Path

from devtools import debug


def deref(linkstr: str, originf: Path):
    try:
        linkstr, part = re.search(r"@(.*?):(.*):*", linkstr).groups()
        if "s/" in part:
            part = re.search(r"(.*):s/.*", part).groups()[0]
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


# def resolve_anything(targetf, part, lang):
#     if "Hymnus" in part:
#         from .H2obj import parse_file
#         hymns = parse_file(targetf, lang)
#         return [hymn for hymn in hymns if hymn.title==]
