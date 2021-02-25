from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDBible(
    CRUDWithOwnerBase[
        models.bible.Verse, schemas.bible.VerseCreate, schemas.bible.VerseUpdate
    ]
):
    pass


bible = CRUDBible(models.bible.Verse)
