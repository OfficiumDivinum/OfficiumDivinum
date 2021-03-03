import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud.base import CreateSchemaType, CRUDType, SchemaType, UpdateSchemaType


def create_item_crud(
    item_schema: SchemaType,
    item_crud: CRUDType,
    item_create_schema: Optional[CreateSchemaType] = None,
    item_update_schema: Optional[UpdateSchemaType] = None,
):
    if not item_create_schema:
        item_create_schema = item_schema
    if not item_update_schema:
        item_update_schema = item_create_schema

    router = APIRouter()

    def filter_dict(filters: Optional[List[str]] = Query(None)):
        try:
            return list(map(json.loads, filters))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid filter input supplied")
        except TypeError:
            pass

    @cbv(router)
    class ItemCBV:
        db: Session = Depends(deps.get_db)
        current_user: models.User = Depends(deps.get_current_active_user)

        @router.get(
            "/",
            response_model=List[item_schema],
            responses={400: {"model": schemas.ErrorMsg}},
        )
        def read_items(
            self,
            skip: int = Query(0, gt=-1),
            limit: int = Query(100, gt=0, lt=200),
            test: List = [2, 4],
            filters: Optional[List] = Depends(filter_dict),
        ) -> Any:
            """Retrieve items."""
            if self.current_user.is_superuser:
                items = item_crud.get_multi(
                    self.db, skip=skip, limit=limit, filters=filters
                )
            else:
                items = item_crud.get_multi_by_owner(
                    db=self.db,
                    owner_id=self.current_user.id,
                    skip=skip,
                    limit=limit,
                    filters=filters,
                )

            return jsonable_encoder(items)

        @router.post(
            "/",
            response_model=item_schema,
            responses={404: {"model": schemas.ErrorMsg}},
        )
        def create_item(self, *, item_in: item_create_schema) -> Any:
            """Create an object, iterating all the way through the supplied schema and
            creating everything as required."""
            item = item_crud.deep_create(
                db=self.db, obj_in=item_in, owner_id=self.current_user.id,
            )
            return jsonable_encoder(item)

        @router.put(
            "/{id}",
            response_model=item_schema,
            responses={404: {"model": schemas.ErrorMsg}},
        )
        def update_item(self, id: int, item_in: item_update_schema,) -> Any:
            """Update an item."""
            item = item_crud.get(db=self.db, id=id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            if not self.current_user.is_superuser and (
                item.owner_id != self.current_user.id
            ):
                raise HTTPException(status_code=400, detail="Not enough permissions")
            item = item_crud.update(db=self.db, db_obj=item, obj_in=item_in)
            return jsonable_encoder(item)

        @router.get(
            "/{id}",
            response_model=item_schema,
            responses={404: {"model": schemas.ErrorMsg}},
        )
        def read_item(self, id: int,) -> Any:
            """Get item by ID."""
            item = item_crud.get(db=self.db, id=id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            if not self.current_user.is_superuser and (
                item.owner_id != self.current_user.id
            ):
                raise HTTPException(status_code=400, detail="Not enough permissions")
            return jsonable_encoder(item)

        @router.delete(
            "/{id}",
            response_model=item_schema,
            responses={404: {"model": schemas.ErrorMsg}},
        )
        def delete_item(self, id: int,) -> Any:
            """Delete an item."""
            item = item_crud.get(db=self.db, id=id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            if not self.current_user.is_superuser and (
                item.owner_id != self.current_user.id
            ):
                raise HTTPException(status_code=400, detail="Not enough permissions")
            item = item_crud.remove(db=self.db, id=id)
            return item  # encoded far end

    return router
