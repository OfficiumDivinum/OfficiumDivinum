from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import schemas
from app.crud.base import CRUDBase, CRUDWithOwnerBase
from app.models.martyrology import Martyrology, OldDateTemplate, Ordinals
from app.schemas.martyrology import MartyrologyCreate, MartyrologyUpdate


class CRUDMartyrology(
    CRUDWithOwnerBase[Martyrology, MartyrologyCreate, MartyrologyUpdate]
):
    def get_by_datestr(self, db: Session, *, datestr: str) -> Optional[Martyrology]:
        return db.query(Martyrology).filter(Martyrology.datestr == datestr)

    def get(self, db: Session, id: int):
        obj = db.query(self.model).get(id)
        obj.render_old_date()
        return obj


martyrology = CRUDMartyrology(Martyrology)


class CRUDOrdinals(
    CRUDWithOwnerBase[
        Ordinals, schemas.martyrology.Ordinals, schemas.martyrology.Ordinals
    ]
):
    pass


ordinals = CRUDOrdinals(Ordinals)


class CRUDOldDateTemplate(
    CRUDWithOwnerBase[
        OldDateTemplate,
        schemas.martyrology.OldDateTemplate,
        schemas.martyrology.OldDateTemplate,
    ]
):
    pass


old_date_template = CRUDOldDateTemplate(OldDateTemplate)
