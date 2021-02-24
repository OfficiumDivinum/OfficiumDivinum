import logging
from datetime import date
from typing import List
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app

from . import get_status
from .item_base import create_item_crud

item_schema = schemas.Martyrology
item_update_schema = schemas.MartyrologyUpdate
item_create_schema = schemas.MartyrologyCreate
item_crud = crud.martyrology

martyrology_router = create_item_crud(
    item_schema, item_crud, item_create_schema, item_update_schema
)

logger = logging.Logger(__name__)

tasks_by_year = {}


def build_association_table(year, taskid):
    """Build association table for given year."""
    get_status.tasks.append(taskid)
    results = celery_app.send_task(
        "app.worker.linear_resolve_martyrology_datestrs", args=[year]
    )
    results.get()
    get_status.tasks.remove(taskid)
    del tasks_by_year[year]


class TaskIDMsg(BaseModel):
    """Response model for taskids."""

    taskid: str


@martyrology_router.get(
    "/date/{date}",
    response_model=List[schemas.Martyrology],
    responses={202: {"model": TaskIDMsg}},
)
async def get_or_generate(
    *,
    db: Session = Depends(deps.get_db),
    date: date,
    background_tasks: BackgroundTasks
    # current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get martyrology by a given date.

    If no such date exists, return a taskid allowing polling until the
    association table is built.
    """
    year = date.year
    date_mdl = models.martyrology.DateTable
    matches = db.query(date_mdl).filter(date_mdl.calendar_date == date).all()
    if len(matches) == 0:
        try:
            taskid = tasks_by_year[year]
            logger.info(f"Already generating for year {year}")
        except KeyError:
            logger.info(f"No matches found, generating for year {year}")
            taskid = str(uuid4())
            background_tasks.add_task(build_association_table, year, taskid)
            tasks_by_year[year] = taskid
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED, content={"taskid": taskid}
        )

    martyrology_objs = []
    for martyrology in (
        db.query(date_mdl).filter(date_mdl.calendar_date == date).one().martyrologies
    ):
        martyrology_objs.append(martyrology)

    return jsonable_encoder(martyrology_objs)


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
