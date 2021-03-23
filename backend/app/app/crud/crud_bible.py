from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDBible(
    CRUDWithOwnerBase[
        models.BibleVerse,
        schemas.bible.BibleVerseCreate,
        schemas.bible.BibleVerseUpdate,
    ]
):
    pass


bible = CRUDBible(models.BibleVerse)
