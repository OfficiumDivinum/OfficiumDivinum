from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDFeast(
    CRUDWithOwnerBase[
        models.bible.Verse, schemas.bible.VerseCreate, schemas.bible.VerseUpdate
    ]
):
    pass


feast = CRUDFeast(models.calendar.Feast)


class CRUDCommemoration(
    CRUDWithOwnerBase[
        models.bible.Verse, schemas.bible.VerseCreate, schemas.bible.VerseUpdate
    ]
):
    pass


commemoration = CRUDCommemoration(models.calendar.Commemoration)
