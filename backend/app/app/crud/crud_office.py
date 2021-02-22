from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.office_parts import Block
from app.schemas.office_parts import BlockCreate, BlockUpdate


class CRUDBlock(CRUDBase[Block, BlockCreate, BlockUpdate]):
    def create(self, db: Session, *, obj_in: BlockCreate) -> Block:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_title(self, db: Session, *, title: str) -> Optional[Block]:
        return db.query(Block).filter(Block.title == title).first()


block = CRUDBlock(Block)
