from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDFeast(
    CRUDWithOwnerBase[models.calendar.Feast, schemas.FeastCreate, schemas.FeastUpdate]
):
    pass


feast = CRUDFeast(models.calendar.Feast)


class CRUDCommemoration(
    CRUDWithOwnerBase[
        models.calendar.Commemoration,
        schemas.CommemorationCreate,
        schemas.CommemorationUpdate,
    ]
):
    pass


commemoration = CRUDCommemoration(models.calendar.Commemoration)
