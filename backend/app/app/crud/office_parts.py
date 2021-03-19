"""
Crud for objects making up an office.

We define these explicitly to make extending easier later.  If we do not
ever extend them, this can all be rolled into a single factory function.
"""
from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDBlock(
    CRUDWithOwnerBase[
        models.Block,
        schemas.BlockCreate,
        schemas.BlockUpdate,
    ]
):
    pass


block = CRUDBlock(models.Block)


class CRUDLine(
    CRUDWithOwnerBase[
        models.Line,
        schemas.LineCreate,
        schemas.LineUpdate,
    ]
):
    pass


line = CRUDLine(models.Line)


class CRUDAntiphon(
    CRUDWithOwnerBase[
        models.Antiphon,
        schemas.AntiphonCreate,
        schemas.AntiphonUpdate,
    ]
):
    pass


antiphon = CRUDAntiphon(models.Antiphon)


class CRUDVersicle(
    CRUDWithOwnerBase[
        models.Versicle,
        schemas.VersicleCreate,
        schemas.VersicleUpdate,
    ]
):
    pass


versicle = CRUDVersicle(models.Versicle)


class CRUDReading(
    CRUDWithOwnerBase[
        models.Reading,
        schemas.ReadingCreate,
        schemas.ReadingUpdate,
    ]
):
    pass


reading = CRUDReading(models.Reading)


class CRUDRubric(
    CRUDWithOwnerBase[
        models.Rubric,
        schemas.RubricCreate,
        schemas.RubricUpdate,
    ]
):
    pass


rubric = CRUDRubric(models.Rubric)
