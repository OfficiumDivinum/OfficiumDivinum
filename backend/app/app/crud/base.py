import logging
from collections import ChainMap
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy_utils.functions import get_mapper

from app.db.base_class import Base

logger = logging.get_logger(__name__)

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
            return db.query(self.model).offset(skip).limit(limit).all()
        else:
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )

    def create_or_match(self, db: Session, obj_in_data, model):
        """
        Match an object if it exists, or if not create one.

        This function is recursive and always returns the outmost
        object.
        """
        db_obj = model()
        query = db.query(db_obj).filter_by(obj_in_data)
        try:
            query.one()
        except MultipleResultsFound:
            logger.info(f"Multiple matches found for {obj_in_data}, using first")
            return query.first()
        except NoResultFound:
            logger.info(f"No matches for {obj_in_data}, creating")
            mapper = get_mapper(db_obj)
            for name, target in mapper.relationships.items():
                if target.secondary:
                    target_model = None  # find a way to get this programmatically
                    target_data = obj_in_data[name]
                    current = getattr(db_obj, name)
                    setattr(
                        db_obj,
                        name,
                        current.append(
                            self.create_or_match(db, target_data, target_model)
                        ),
                    )
                    del obj_in_data[name]
            db_obj.update(obj_in_data)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
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
        db.delete(obj)
        db.commit()
        return obj


CRUDType = TypeVar("CRUDType", bound=CRUDBase)


class CRUDWithOwnerBase(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def create_with_owner(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
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
