import json
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.martyrology import Martyrology
from app.schemas.martyrology import MartyrologyCreate, MartyrologyUpdate


class CRUDMartyrology(CRUDBase[Martyrology, MartyrologyCreate, MartyrologyUpdate]):
    def create(self, db: Session, *, obj_in: MartyrologyCreate) -> Martyrology:
        obj_in_data = jsonable_encoder(obj_in)
        print(json.dumps(obj_in_data, indent=2))
        db_obj = self.model(**obj_in_data)
        print(jsonable_encoder(db_obj))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_datestr(self, db: Session, *, datestr: str) -> Optional[Martyrology]:
        return db.query(Martyrology).filter(Martyrology.datestr == datestr)

    def get(self, db: Session, id: int):
        obj = db.query(self.model).get(id)
        obj.render_old_date()
        return obj


martyrology = CRUDMartyrology(Martyrology)
