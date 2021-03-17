from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDBible(
    CRUDWithOwnerBase[
        models.bible.BibleVerse,
        schemas.bible.BibleVerseCreate,
        schemas.bible.BibleVerseUpdate,
    ]
):
    pass


bible = CRUDBible(models.bible.BibleVerse)
