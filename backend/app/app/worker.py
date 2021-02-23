from datetime import date
from typing import List

from celery import group
from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings
from app.DSL import dsl_parser

client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def resolve_datestr(datestr: str, year: int) -> date:
    return dsl_parser(datestr, year)


@celery_app.task()
def resolve_datestrs(datestrs: List[str], year: int) -> List[date]:
    return group((linear_resolve_datestrs.s(i, year) for i in datestrs))()


@celery_app.task()
def linear_resolve_datestrs(datestrs, year):
    resolved = (dsl_parser(i, year) for i in datestrs)
