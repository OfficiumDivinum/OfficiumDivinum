from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# @router.get("/", response_model=List[schemas.Block])
# def read_items(
#     db: Session = Depends(deps.get_db),
#     skip: int = 0,
#     limit: int = 100,
# ) -> Any:
#     """Retrieve items."""
#     items = crud.crud_office.get_by(db, skip=skip, limit=limit)
#     else:
#         items = crud.item.get_multi_by_owner(
#             db=db, owner_id=current_user.id, skip=skip, limit=limit
#         )
#     return items


@router.post("/", response_model=schemas.Block)
def create_item(
    *, db: Session = Depends(deps.get_db), item_in: schemas.BlockCreate,
) -> Any:
    """Create new item."""
    block = crud.block.create(db=db, obj_in=item_in)
    return block


@router.get("/{title}", response_model=schemas.Block)
def read_item(*, db: Session = Depends(deps.get_db), title: str,) -> Any:
    """Get item by ID."""
    item = crud.block.get_by_title(db=db, title=title)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# @router.put("/{id}", response_model=schemas.Item)
# def update_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     item_in: schemas.ItemUpdate,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """Update an item."""
#     item = crud.item.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
#     return item


# @router.delete("/{id}", response_model=schemas.Item)
# def delete_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """Delete an item."""
#     item = crud.item.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = crud.item.remove(db=db, id=id)
#     return item
