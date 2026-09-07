from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_optional_user, require_admin
from ..database import get_db
from ..models import AdminUser, Category, GiftItem
from ..schemas import GiftItemCreate, GiftItemOut, GiftItemUpdate

router = APIRouter(prefix="/api/gift-items", tags=["gift-items"])


@router.get("", response_model=list[GiftItemOut])
def list_items(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    user: Optional[AdminUser] = Depends(get_optional_user),
) -> list[GiftItem]:
    query = db.query(GiftItem)
    if include_inactive:
        if user is None or not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito.")
    else:
        query = query.filter(GiftItem.active.is_(True))
    return query.order_by(GiftItem.display_order).all()


@router.post("", response_model=GiftItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: GiftItemCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> GiftItem:
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=400, detail="Categoria inválida.")
    item = GiftItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=GiftItemOut)
def update_item(
    item_id: str,
    payload: GiftItemUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> GiftItem:
    item = db.get(GiftItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    updates = payload.model_dump(exclude_unset=True)
    if "category_id" in updates and db.get(Category, updates["category_id"]) is None:
        raise HTTPException(status_code=400, detail="Categoria inválida.")

    for key, value in updates.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> None:
    item = db.get(GiftItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    db.delete(item)
    db.commit()
