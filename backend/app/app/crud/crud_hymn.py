from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDHymnVerse(
    CRUDWithOwnerBase[
        models.hymn.Verse, schemas.hymn.VerseCreate, schemas.bible.VerseUpdate
    ]
):
    pass


verse = CRUDHymnVerse(models.hymn.Verse)


class CRUDHymnHymn(
    CRUDWithOwnerBase[
        models.hymn.Hymn, schemas.hymn.HymnCreate, schemas.bible.HymnUpdate
    ]
):
    pass


hymn = CRUDHymnHymn(models.hymn.Hymn)
