import logging
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.versions import versions_dict

from . import get_status
from .item_base import create_item_crud

logger = logging.getLogger(__name__)

tasks_by_year = {}


def build_association_table(year, taskid):
    """
    Build association table for given year.

    Args:
      year:
      taskid:

    Returns:
    """
    get_status.tasks.append(taskid)
    results = celery_app.send_task("app.worker.linear_resolve_datestrs", args=[year])
    results.get()
    get_status.tasks.remove(taskid)
    del tasks_by_year[year]


router = APIRouter()

commemoration_router = create_item_crud(
    schemas.Commemoration, crud.commemoration, schemas.CommemorationCreate
)
router.include_router(commemoration_router, prefix="/commemoration")

feast_router = create_item_crud(schemas.Feast, crud.feast, schemas.FeastCreate)

router.include_router(feast_router, prefix="/feast")


@router.get(
    "/date/{date}",
    response_model=schemas.Feast,
    responses={202: {"model": schemas.TaskIDMsg}},
)
async def get_or_generate(
    date: date,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    version: str = "1960",
):
    """"""

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

    feast_objs = []
    for feast in db.query(date_mdl).filter(date_mdl.calendar_date == date).one().feasts:
        feast_objs.append(feast)
    print(feast_objs)
    feast = versions_dict[version].resolve(*feast_objs)
    return jsonable_encoder(feast)
