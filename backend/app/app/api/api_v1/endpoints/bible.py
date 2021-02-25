from app import crud, schemas

from .item_base import create_item_crud

router = create_item_crud(
    schemas.bible.Verse,
    crud.bible,
    schemas.bible.VerseCreate,
    schemas.bible.VerseUpdate,
)
