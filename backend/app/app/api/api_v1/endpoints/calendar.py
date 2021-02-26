from fastapi import APIRouter

from app import crud, schemas

from .item_base import create_item_crud

router = APIRouter()

commemoration_router = create_item_crud(
    schemas.Commemoration, crud.commemoration, schemas.CommemorationCreate
)
router.include_router(commemoration_router, prefix="/commemoration")

feast_router = create_item_crud(schemas.Feast, crud.feast, schemas.FeastCreate)

router.include_router(feast_router, prefix="/feast")
