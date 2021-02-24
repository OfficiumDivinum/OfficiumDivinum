import logging

from raven import Client

from app import models
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.DSL import dsl_parser

logger = logging.getLogger(__name__)
client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def linear_resolve_martyrology_datestrs(year):
    """Resolve datestrs for martyrologies for given year."""

    date_mdl = models.martyrology.DateTable
    db = SessionLocal()
    matches = db.query(models.Martyrology)
    datestrs = [i.datestr for i in matches]
    logger.debug(f"Found {len(list(datestrs))} datestrs to resolve.")

    resolved = [dsl_parser(i, year) for i in datestrs]

    logger.debug(f"resolved {len(resolved)}")

    date_objs = {}
    for calendar_date in set(resolved):
        mdl = date_mdl(calendar_date=calendar_date)
        db.add(mdl)
        date_objs[calendar_date] = mdl

    for martyrology, calendar_date in zip(matches, resolved):
        calendar_date = date_objs[calendar_date]
        martyrology.dates.append(calendar_date)

    db.commit()
