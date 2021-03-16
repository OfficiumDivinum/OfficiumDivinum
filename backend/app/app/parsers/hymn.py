"""Get all Hymns from Divinumofficium's source files."""
from pathlib import Path
from typing import Union

from devtools import debug
from pydantic.error_wrappers import ValidationError

from app.parsers import util
from app.parsers.util import Thing
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
