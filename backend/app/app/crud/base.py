import logging
from collections import ChainMap, Iterable
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from devtools import debug
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy_utils.functions import get_class_by_table, get_mapper

from app.db.base_class import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


def clear_debug(*args):
    print("\n\n\n")
    debug(*args)
    print("\n\n\n")


# def clear_debug(*args):
#     pass


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
        debug("Calling get multi")
        if not filters:
            obj = db.query(self.model).offset(skip).limit(limit).all()
            debug(jsonable_encoder(obj))
            return obj

        else:
            debug(filters)
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )

    def create_or_match(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int, model=None
    ):
        # print("=====Start=====")
        obj = self.create_or_match_loopfn(
            db, obj_in=obj_in, owner_id=owner_id, model=model
        )
        db.commit()
        # print("=====End=====")
        # get the object anew so we have all the content
        debug(model)
        obj = db.query(self.model).filter(self.model.id == obj.id).first()
        debug(jsonable_encoder(obj))
        # debug(obj.parts)
        return jsonable_encoder(obj)

    def _relationship_test(self, db: Session, db_obj, obj_in):
        """
        Test whether or no all the relationships of db_obj map correctly onto objects of
        obj_in.

        This function is recursive. Hopefully sqlalchemy caches the
        query in the session...
        """
        debug("Called with", db_obj, obj_in)
        mapper = get_mapper(db_obj)
        skip_keys = ["owner", "owner_id"]
        for name, target in mapper.relationships.items():
            if name in skip_keys:
                continue
            try:
                target_data = getattr(obj_in, name)
            except AttributeError:
                debug(f"Could not find {name} in obj_in")
                continue  # for now

            if not target_data:
                debug(f"Input was blank for entry {name}, but db_obj has {target}")
                continue  # for now

            # get target obj from db
            if not isinstance(target_data, Iterable):
                target_data = [target_data]

            model = get_class_by_table(Base, target.target)

            for entry in target_data:
                debug(entry, name)
                safe_filter = self._safe_filter(entry)
                db_obj = db.query(model).filter_by(**safe_filter).one()

                debug("Calling self with", db_obj, target_data)
                if not self._relationship_test(db, db_obj, entry):
                    debug("Returning False")
                    return False

        for key, val in mapper.attrs.items():
            debug(key, val)
            if key in skip_keys:
                continue
            if getattr(obj_in, key) != val:
                debug("Returning False")
                return False

            # # for entry in target_data:
            # for attr in getattr(db_obj, name):
            #     m = get_mapper(attr)
            #     debug(m.relationships)

        debug("Returning True")
        return True

    @staticmethod
    def _safe_filter(obj_in: Any):
        """
        Generates a filter consisting only of properties which we can actually filter
        with.

        Args:
          obj_in: Any: The obj containing the properties to filter.

        Returns:
          A filter dict, all ready for filter_by()
        """
        safe_filter = {
            k: v
            for k, v in dict(obj_in).items()
            if any(
                (
                    isinstance(v, str),
                    isinstance(v, int),
                    isinstance(v, float),
                    isinstance(v, bool),
                ),
            )
        }
        return safe_filter

    def create_or_match_loopfn(
        self, db: Session, *, obj_in: Any, owner_id: int, model=None
    ):
        """
        Matches an object if it exists, or if not creates one.

        This function is recursive and always returns the outmost
        object.

        Args:
          db: Session: The db session to use.  We reuse a session.
          obj_in: Any: Obj in.  Any introspectable obj (e.g. schema, dict).
          owner_id: int: The owner.
          model:  (Default value = None) The model to use.
                  Only none in the outermost scope, when we use the self.model.

        Returns:
          An sqlalchemy object representing the obj created.
        """
        debug("Starting loop")
        if not model:
            model = self.model

        debug(obj_in)
        safe_filter = self._safe_filter(obj_in)
        db_obj = model(owner_id=owner_id)

        debug("Querying", safe_filter)
        query = db.query(model).filter_by(**safe_filter)
        try:
            d = query.one()
            mapper = get_mapper(d)
            # does the model have relationships?
            # we don't use a joined query as we don't know how deep the relationships go, and we want to handle any depth.
            # if mapper.relationships:
            #     # check *every single relationship* and make a whole new object if not.
            #     if self._relationship_test(db, d, obj_in):
            #         debug("Found exact match", mapper.attrs)
            #         return d
            return d
        except MultipleResultsFound:
            logger.info("Multiple matches found, using first", safe_filter)
            debug("Multiple matches found, using first", safe_filter)
            d = query.first()
            return d
        except NoResultFound:
            logger.info("No matches found, creating", safe_filter)
            debug("No matches found, creating", safe_filter)
            debug("mapping")
            mapper = get_mapper(db_obj)
            for name, target in mapper.relationships.items():
                debug(f"Creating target {name} of type {target}")
                if target.secondary is not None:
                    debug("Target has secondary table.")
                    target_model = get_class_by_table(Base, target.target)
                    try:
                        target_data = getattr(obj_in, name)
                    except AttributeError:
                        debug("Input has no value, skipping")
                        continue
                    if not target_data:
                        debug("Input value is empty, skipping")
                        continue
                    for entry in target_data:
                        debug("Getting current data")
                        current = getattr(db_obj, name)

                        debug("Looping to create or match entry", entry)
                        new = self.create_or_match_loopfn(
                            db, obj_in=entry, owner_id=owner_id, model=target_model
                        )
                        if new in current:
                            # always duplicate identical lines
                            new = target_model(**jsonable_encoder(entry))
                        current.append(new)

                    setattr(db_obj, name, current)

                    delattr(obj_in, name)

                else:
                    debug(
                        f"Making or getting non many-to-many object {name} of type {target}"
                    )
                    target_model = get_class_by_table(Base, target.target)
                    try:
                        target_data = getattr(obj_in, name)
                    except AttributeError:
                        continue
                    if not target_data:
                        continue

                    new = self.create_or_match_loopfn(
                        db, obj_in=target_data, owner_id=owner_id, model=target_model
                    )

                    setattr(db_obj, name, new)
                    delattr(obj_in, name)
                # else:
                #     debug(f"Got here, need to make obj {target.target}")

        for k, v in obj_in:
            # print(f"k: {k}, v: {v}")
            try:
                setattr(db_obj, k, v)
            except (TypeError, AttributeError):
                pass
        db.add(db_obj)

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
        db.delete(obj)
        db.commit()
        return obj


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
