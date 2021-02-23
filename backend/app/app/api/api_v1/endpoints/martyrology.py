from fastapi import Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas, worker
from app.api import deps
from app.core.celery_app import celery_app

from .item_base import create_item_crud

item_schema = schemas.Martyrology
item_update_schema = schemas.MartyrologyUpdate
item_create_schema = schemas.MartyrologyCreate
item_crud = crud.martyrology

martyrology_router = create_item_crud(
    item_schema, item_crud, item_create_schema, item_update_schema
)


@martyrology_router.get("/test-datestr/{year}")
def gen_datestrs(
    *,
    db: Session = Depends(deps.get_db),
    year: int
    # current_user: models.User = Depends(deps.get_current_active_user),
):
    db_obj = db.query(models.Martyrology).distinct("datestr")
    # db_obj = list(db_obj)[:100]
    datestrs = [i.datestr for i in db_obj]
    # chunks = []
    # for i in range(len(datestrs) // 100):
    #     chunks.append(datestrs[i * 100 : i * 100 + 100])
    # print(chunks)
    # results = celery_app.send_task("app.worker.resolve_datestrs", args=[chunks, year])
    # results.get()
    # calendar_dates = [i.get() for i in results.children[0]]
    results = celery_app.send_task(
        "app.worker.linear_resolve_datestrs", args=[[i.datestr for i in db_obj], year]
    )
    calendar_dates = results.get()
    mapping = {}
    for i, date in enumerate(calendar_dates):
        try:
            mapping[date].append(datestrs[i])
        except KeyError:
            mapping[date] = [datestrs[i]]
    return mapping

    # return res


ordinals_router = create_item_crud(schemas.Ordinals, crud.ordinals)

martyrology_router.include_router(
    ordinals_router, prefix="/ordinals",
)

old_date_template_router = create_item_crud(
    schemas.OldDateTemplate, crud.old_date_template, schemas.OldDateTemplateCreate
)

martyrology_router.include_router(
    old_date_template_router, prefix="/old-date-template",
)
