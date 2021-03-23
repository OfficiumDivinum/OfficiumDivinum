from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDHymnVerse(
    CRUDWithOwnerBase[
        models.HymnVerse, schemas.hymn.VerseCreate, schemas.hymn.VerseUpdate
    ]
):
    pass


hymn_verse = CRUDHymnVerse(models.HymnVerse)


class CRUDHymnHymn(
    CRUDWithOwnerBase[models.Hymn, schemas.hymn.HymnCreate, schemas.hymn.HymnUpdate]
):
    pass


hymn = CRUDHymnHymn(models.Hymn)
