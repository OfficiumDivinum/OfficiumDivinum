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
