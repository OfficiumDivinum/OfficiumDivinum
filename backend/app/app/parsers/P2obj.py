"""Parse Divinumofficium's psalm files into Psalm objects."""

import re
from pathlib import Path

from app.schemas.bible import VerseCreate


def parse_file(fn: Path, lang: str, version: str) -> VerseCreate:
    """Parse a Divinumofficium psalm file."""

    verses = []
    with fn.open() as f:
        for line in f.readlines():
            try:
                chapter, verseno, verse = re.search(
                    r"([0-9]+):([0-9]+) (.*)", line
                ).groups()
                verse = VerseCreate(
                    language=lang,
                    version=version,
                    book="Psalm",
                    prefix=f"{fn.stem}:{verseno}",
                    content=verse,
                    suffix=None,
                )
                verses.append(verse)
            except AttributeError:
                raise Exception(f"Failed to parse line {line.strip()}")
    return verses
