"""Parse Divinumofficium's psalm files into Psalm objects."""

import re
from pathlib import Path

from app.schemas.bible import VerseCreate


def parse_file(fn: Path, lang: str, version: str) -> VerseCreate:
    """Parse a Divinumofficium psalm file."""

    verses = []
    aka = None
    book = "Psalm"
    with fn.open() as f:
        for line in f.readlines():
            try:
                chapter, verseno, verse = re.search(
                    r"([0-9]+):([0-9]+) (.*)", line
                ).groups()
            except AttributeError:
                # we have a funy psalm
                try:
                    aka, book, chapter, versenos = re.search(
                        r"\((.*?) *[\*:] (.*?) (.*?):(.*?)\)", line
                    ).groups()
                    continue
                except AttributeError:
                    f.close()
                    return parse_creed(fn, lang, version)
                    # aka, other = re.search(r"\((.*) \* (.*)\)", line).groups()
                    # aka = aka.strip()
                    # book = None
                    # continue
            verse = VerseCreate(
                language=lang,
                version=version,
                book=book,
                prefix=f"{fn.stem}:{verseno}",
                content=verse,
                suffix=None,
                aka=aka,
            )
            verses.append(verse)
    return verses


def parse_creed(fn: Path, lang, version):
    verses = []
    with fn.open() as f:
        lines = f.readlines()
    aka = lines[0]
    for line in lines[1:]:
        verse = VerseCreate(
            language=lang,
            version=version,
            content=line,
            suffix=None,
            aka=aka,
            book=None,
        )
        verses.append(verse)
    return verses
