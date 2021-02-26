import logging
from datetime import date
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.versions import versions_dict

from .calendar import build_association_table, tasks_by_year
from .item_base import create_item_crud

martyrology_router = create_item_crud(
    schemas.Martyrology,
    crud.martyrology,
    schemas.MartyrologyCreate,
    schemas.MartyrologyUpdate,
)

logger = logging.Logger(__name__)


@martyrology_router.get(
    "/date/{date}",
    response_model=schemas.Martyrology,
    responses={202: {"model": schemas.TaskIDMsg}},
)
async def get_or_generate(
    *,
    db: Session = Depends(deps.get_db),
    date: date,
    version: str = "1960",
    background_tasks: BackgroundTasks,
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
        print("id", martyrology.id)
        martyrology_objs.append(martyrology)
    mart = versions_dict[version].resolve(*martyrology_objs)
    mart.render_old_date(year)
    return jsonable_encoder(mart)


ordinals_router = create_item_crud(
    schemas.Ordinals, crud.ordinals, schemas.OrdinalsCreate
)

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
