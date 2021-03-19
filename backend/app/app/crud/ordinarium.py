"""
Crud for offices themselves.

As usual we are verbose here.
"""
from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDCompline(
    CRUDWithOwnerBase[
        models.Compline,
        schemas.ComplineCreate,
        schemas.ComplineUpdate,
    ]
):
    pass


compline = CRUDCompline(models.Compline)
