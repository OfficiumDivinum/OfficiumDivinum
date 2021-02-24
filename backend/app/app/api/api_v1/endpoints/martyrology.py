import logging
from datetime import date
from typing import List

from fastapi import Depends
from sqlalchemy import inspect
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.db.base_class import Base
from app.models import tablelist

from .item_base import create_item_crud

item_schema = schemas.Martyrology
item_update_schema = schemas.MartyrologyUpdate
item_create_schema = schemas.MartyrologyCreate
item_crud = crud.martyrology

martyrology_router = create_item_crud(
    item_schema, item_crud, item_create_schema, item_update_schema
)

logger = logging.Logger(__name__)


def chunker(iterable, size):
    chunks = []
    for i in range(0, len(iterable), size):
        chunks.append(iterable[i : (i + size)])
    return chunks


@martyrology_router.get(
    "/test-datestr/{date}", response_model=List[schemas.Martyrology]
)
async def gen_datestrs(
    *,
    db: Session = Depends(deps.get_db),
    date: date,
    # current_user: models.User = Depends(deps.get_current_active_user),
):
    year = date.year
    date_mdl = models.martyrology.DateTable
    matches = db.query(date_mdl).filter(date_mdl.calendar_date == date).all()
    if len(matches) == 0:
        logger.info(f"No matches found, generating for year {date.year}")

        results = celery_app.send_task(
            "app.worker.linear_resolve_martyrology_datestrs", args=[year]
        )
        results.get()

        # calendar_dates = []
        # for chunk in results.children:
        #     calendar_dates += chunk.get()[0]

        # date_objs = {}
        # for calendar_date in set(calendar_dates):
        #     mdl = date_mdl(calendar_date=calendar_date)
        #     db.add(mdl)
        #     date_objs[calendar_date] = mdl
        # print(db.dirty)

        # for martyrology, calendar_date in zip(matches, calendar_dates):
        #     calendar_date = date_objs[calendar_date]
        #     martyrology.dates.append(calendar_date)

        # db.commit()

    martyrology_objs = []
    for martyrology in (
        db.query(date_mdl).filter(date_mdl.calendar_date == date).one().martyrologies
    ):
        martyrology_objs.append(martyrology)

    return martyrology_objs


ordinals_router = create_item_crud(schemas.Ordinals, crud.ordinals)

martyrology_router.include_router(
    ordinals_router,
    prefix="/ordinals",
)

old_date_template_router = create_item_crud(
    schemas.OldDateTemplate, crud.old_date_template, schemas.OldDateTemplateCreate
)

martyrology_router.include_router(
    old_date_template_router,
    prefix="/old-date-template",
)
