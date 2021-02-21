from app import crud, schemas

from .item_base import create_item_crud

item_schema = schemas.Martyrology
item_update_schema = schemas.MartyrologyUpdate
item_create_schema = schemas.MartyrologyCreate
item_crud = crud.martyrology

martyrology_router = create_item_crud(
    item_schema, item_crud, item_update_schema, item_create_schema
)

ordinals_router = create_item_crud(schemas.Ordinals, crud.ordinals)

martyrology_router.include_router(
    ordinals_router,
    prefix="/ordinals",
    tags=["martyrology"],
)

old_date_template_router = create_item_crud(
    schemas.OldDateTemplate, crud.old_date_template
)
martyrology_router.include_router(
    old_date_template_router,
    prefix="/old-date-template",
    tags=["old date template"],
)
