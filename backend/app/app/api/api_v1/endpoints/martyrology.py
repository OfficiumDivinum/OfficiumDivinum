import logging
from datetime import date
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.versions import versions_dict

from . import get_status
from .item_base import create_item_crud

martyrology_router = create_item_crud(
    schemas.Martyrology,
    crud.martyrology,
    schemas.MartyrologyUpdate,
    schemas.MartyrologyCreate,
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
    response_model=schemas.Martyrology,
    responses={202: {"model": TaskIDMsg}},
)
async def get_or_generate(
    *,
    db: Session = Depends(deps.get_db),
    date: date,
    version: str = "1960",
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

    return jsonable_encoder(versions_dict[version].resolve(*martyrology_objs))


# @martyrology_router.delete("/datetable/clear")
# async def delete_datetable(
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ):
#     """Clear the datetable entirely."""
#     for row in db.query(models.martyrology.DateTable).all():
#         row.martyrologies = []
#         db.commit()
#     return True


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
