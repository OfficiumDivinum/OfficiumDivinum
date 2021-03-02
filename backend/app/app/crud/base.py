import logging
from collections import ChainMap
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from devtools import debug
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy_utils.functions import get_class_by_table, get_mapper

from app.db.base_class import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Dict]] = None,
    ) -> List[ModelType]:
        if not filters:
            obj = db.query(self.model).offset(skip).limit(limit).all()
            return obj

        else:
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )

    def deep_create(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int, model=None
    ):
        obj = self.create_loopfn(db, obj_in=obj_in, owner_id=owner_id, model=model)
        db.add(obj)
        db.commit()
        # # get the object anew so we have all the content
        obj = db.query(self.model).filter(self.model.id == obj.id).one()
        return jsonable_encoder(obj)

    def create_loopfn(self, db: Session, *, obj_in: Any, owner_id: int, model=None):
        """
        Creates an object of arbitrary nested depth.

        This function is recursive and always returns the outmost
        object.

        Args:
          db: Session: The db session to use.  We reuse a session.
          obj_in: Any: Obj in.  Any introspectable obj (e.g. schema, dict).
          owner_id: int: The owner.
          model:  (Default value = None) The model to use.
                  Only none in the outermost scope, when we use self.model.

        Returns:
          An sqlalchemy object representing the obj created.
        """
        if not model:
            model = self.model

        db_obj = model(owner_id=owner_id)

        mapper = get_mapper(db_obj)

        for name, target in mapper.relationships.items():

            target_model = get_class_by_table(Base, target.target)

            try:
                target_data = getattr(obj_in, name)
            except AttributeError:
                # debug(f"Input not supplied for {name}, skipping")
                continue
            if not target_data:
                # debug(f"Input value for {name} is empty, skipping")
                continue

            if target.secondary is not None:

                objs = []
                for entry in target_data:

                    obj = self.create_loopfn(
                        db, obj_in=entry, owner_id=owner_id, model=target_model
                    )
                    objs.append(obj)

                setattr(db_obj, name, objs)

                # delete so we can loop over remaining properties later
                delattr(obj_in, name)

            else:
                # debug(
                #     "Making or getting non many-to-many object"
                #     f"{name} of type {target}"
                # )

                new = self.create_loopfn(
                    db, obj_in=target_data, owner_id=owner_id, model=target_model
                )

                setattr(db_obj, name, new)
                delattr(obj_in, name)

        for k, v in obj_in:
            try:
                setattr(db_obj, k, v)
            except (TypeError, AttributeError):
                pass
        # db.add(db_obj)

        return db_obj

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        obj_copy = jsonable_encoder(obj)
        db.delete(obj)
        db.commit()
        return obj_copy


CRUDType = TypeVar("CRUDType", bound=CRUDBase)


class CRUDWithOwnerBase(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def create_with_owner(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self,
        db: Session,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Dict]] = None,
    ) -> List[ModelType]:
        if not filters:
            return (
                db.query(self.model)
                .filter(self.model.owner_id == owner_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter(self.model.owner_id == owner_id)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )
