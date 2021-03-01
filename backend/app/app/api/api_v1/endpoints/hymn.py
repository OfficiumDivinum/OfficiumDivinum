from app import crud, schemas

from .item_base import create_item_crud

router = create_item_crud(
    schemas.Hymn, crud.hymn, schemas.hymn.HymnCreate, schemas.hymn.HymnUpdate
)

verse_router = create_item_crud(
    schemas.hymn.Verse,
    crud.hymn_verse,
    schemas.hymn.VerseCreate,
    schemas.hymn.HymnUpdate,
)
router.include_router(verse_router, prefix="/verse")
