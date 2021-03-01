from app import crud, schemas

from .item_base import create_item_crud

hymn_router = create_item_crud(
    schemas.Hymn, crud.hymn.Hymn, schemas.hymn.HymnCreate, schemas.hymn.HymnUpdate
)

verse_router = create_item_crud(
    schemas.hymn.Verse, crud.hymn, schemas.hymn.VerseCreate, schemas.hymn.HymnUpdate
)
hymn_router.include_router(verse_router, prefix="/verse")
