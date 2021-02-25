from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    bible,
    get_status,
    items,
    login,
    martyrology,
    users,
    utils,
)

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
