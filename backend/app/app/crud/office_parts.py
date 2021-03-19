"""
Crud for objects making up an office.

We define these explicitly to make extending easier later.  If we do not
ever extend them, this can all be rolled into a single factory function.
"""
from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDBlock(
    CRUDWithOwnerBase[
        models.office_parts.Block,
        schemas.office_parts.BlockCreate,
        schemas.office_parts.BlockUpdate,
    ]
):
    pass


block = CRUDBlock(models.office_parts.Block)


class CRUDLine(
    CRUDWithOwnerBase[
        models.office_parts.Line,
        schemas.office_parts.LineCreate,
        schemas.office_parts.LineUpdate,
    ]
):
    pass


line = CRUDLine(models.office_parts.Line)


class CRUDAntiphon(
    CRUDWithOwnerBase[
        models.office_parts.Antiphon,
        schemas.office_parts.AntiphonCreate,
        schemas.office_parts.AntiphonUpdate,
    ]
):
    pass


antiphon = CRUDAntiphon(models.office_parts.Antiphon)


class CRUDVersicle(
    CRUDWithOwnerBase[
        models.office_parts.Versicle,
        schemas.office_parts.VersicleCreate,
        schemas.office_parts.VersicleUpdate,
    ]
):
    pass


versicle = CRUDVersicle(models.office_parts.Versicle)


class CRUDReading(
    CRUDWithOwnerBase[
        models.office_parts.Reading,
        schemas.office_parts.ReadingCreate,
        schemas.office_parts.ReadingUpdate,
    ]
):
    pass


reading = CRUDReading(models.office_parts.Reading)


class CRUDRubric(
    CRUDWithOwnerBase[
        models.office_parts.Rubric,
        schemas.office_parts.RubricCreate,
        schemas.office_parts.RubricUpdate,
    ]
):
    pass


rubric = CRUDRubric(models.office_parts.Rubric)
