from fastapi import APIRouter

from app import crud, schemas
from app.api.api_v1.endpoints import (
    bible,
    calendar,
    get_status,
    hymn,
    items,
    login,
    martyrology,
    users,
    utils,
)
from app.api.api_v1.endpoints.item_base import create_item_crud

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    martyrology.martyrology_router, prefix="/martyrology", tags=["martyrology"]
)
api_router.include_router(
    get_status.router, prefix="/in-progress", tags=["in progress"]
)

api_router.include_router(bible.router, prefix="/bible", tags=["bible"])

api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])

api_router.include_router(hymn.router, prefix="/hymn", tags=["hymn"])

antiphon_router = create_item_crud(
    schemas.Antiphon,
    crud.antiphon,
    schemas.AntiphonCreate,
    schemas.AntiphonUpdate,
)
api_router.include_router(antiphon_router, prefix="/antiphon", tags=["antiphon"])

versicle_router = create_item_crud(
    schemas.Versicle,
    crud.versicle,
    schemas.VersicleCreate,
    schemas.VersicleUpdate,
)
api_router.include_router(versicle_router, prefix="/versicle", tags=["versicle"])

reading_router = create_item_crud(
    schemas.Reading,
    crud.reading,
    schemas.ReadingCreate,
    schemas.ReadingUpdate,
)
api_router.include_router(reading_router, prefix="/reading", tags=["reading"])

rubric_router = create_item_crud(
    schemas.Rubric,
    crud.rubric,
    schemas.RubricCreate,
    schemas.RubricUpdate,
)
api_router.include_router(rubric_router, prefix="/rubric", tags=["rubric"])
