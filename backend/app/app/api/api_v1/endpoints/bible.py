from app import crud, schemas

from .item_base import create_item_crud

router = create_item_crud(
    schemas.bible.BibleVerse,
    crud.bible,
    schemas.bible.BibleVerseCreate,
    schemas.bible.BibleVerseUpdate,
)
