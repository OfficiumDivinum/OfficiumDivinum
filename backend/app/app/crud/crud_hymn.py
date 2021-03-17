from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDHymnVerse(
    CRUDWithOwnerBase[
        models.hymn.HymnVerse, schemas.hymn.VerseCreate, schemas.hymn.VerseUpdate
    ]
):
    pass


hymn_verse = CRUDHymnVerse(models.hymn.HymnVerse)


class CRUDHymnHymn(
    CRUDWithOwnerBase[
        models.hymn.Hymn, schemas.hymn.HymnCreate, schemas.hymn.HymnUpdate
    ]
):
    pass


hymn = CRUDHymnHymn(models.hymn.Hymn)
