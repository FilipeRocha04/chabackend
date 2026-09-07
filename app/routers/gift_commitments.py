from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import AdminUser, GiftCommitment, GiftItem
from ..schemas import GiftCommitmentBulkCreate, GiftCommitmentCreate, GiftCommitmentOut

router = APIRouter(prefix="/api/gift-commitments", tags=["gift-commitments"])


@router.post("", response_model=GiftCommitmentOut, status_code=status.HTTP_201_CREATED)
def create_commitment(payload: GiftCommitmentCreate, db: Session = Depends(get_db)) -> GiftCommitment:
    item = db.get(GiftItem, payload.gift_item_id)
    if item is None or not item.active:
        raise HTTPException(status_code=400, detail="Este item não está disponível.")

    already = (
        db.query(func.sum(GiftCommitment.quantity))
        .filter(GiftCommitment.gift_item_id == item.id)
        .scalar()
        or 0
    )
    remaining = item.desired_quantity - already
    if payload.quantity > remaining:
        raise HTTPException(
            status_code=400,
            detail=f'Restam apenas {max(remaining, 0)} unidade(s) de "{item.name}".',
        )

    guest_name = payload.guest_name.strip()[:60] or None
    commitment = GiftCommitment(
        gift_item_id=payload.gift_item_id,
        guest_name=guest_name,
        quantity=payload.quantity,
    )
    db.add(commitment)
    db.commit()
    db.refresh(commitment)
    return commitment


@router.post("/bulk", response_model=list[GiftCommitmentOut], status_code=status.HTTP_201_CREATED)
def create_commitments_bulk(
    payload: GiftCommitmentBulkCreate, db: Session = Depends(get_db)
) -> list[GiftCommitment]:
    item_ids = [entry.gift_item_id for entry in payload.items]
    items = db.query(GiftItem).filter(GiftItem.id.in_(item_ids)).all()
    items_by_id = {item.id: item for item in items}

    for entry in payload.items:
        item = items_by_id.get(entry.gift_item_id)
        if item is None or not item.active:
            raise HTTPException(status_code=400, detail="Um dos itens escolhidos não está disponível.")

    committed_rows = (
        db.query(GiftCommitment.gift_item_id, func.sum(GiftCommitment.quantity))
        .filter(GiftCommitment.gift_item_id.in_(item_ids))
        .group_by(GiftCommitment.gift_item_id)
        .all()
    )
    committed_by_id = {gift_item_id: int(total) for gift_item_id, total in committed_rows}

    requested_by_id: dict[str, int] = {}
    for entry in payload.items:
        requested_by_id[entry.gift_item_id] = requested_by_id.get(entry.gift_item_id, 0) + entry.quantity

    for item_id, requested in requested_by_id.items():
        item = items_by_id[item_id]
        already = committed_by_id.get(item_id, 0)
        remaining = item.desired_quantity - already
        if requested > remaining:
            raise HTTPException(
                status_code=400,
                detail=f'Restam apenas {max(remaining, 0)} unidade(s) de "{item.name}".',
            )

    guest_name = payload.guest_name.strip()[:60] or None
    commitments = [
        GiftCommitment(
            gift_item_id=entry.gift_item_id,
            guest_name=guest_name,
            quantity=entry.quantity,
        )
        for entry in payload.items
    ]
    db.add_all(commitments)
    db.commit()
    for commitment in commitments:
        db.refresh(commitment)
    return commitments


@router.get("", response_model=list[GiftCommitmentOut])
def list_commitments(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> list[GiftCommitment]:
    return db.query(GiftCommitment).order_by(GiftCommitment.created_at.desc()).all()


@router.delete("/{commitment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_commitment(
    commitment_id: str,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> None:
    commitment = db.get(GiftCommitment, commitment_id)
    if commitment is None:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    db.delete(commitment)
    db.commit()


totals_router = APIRouter(prefix="/api/gift-totals", tags=["gift-commitments"])


@totals_router.get("")
def gift_totals(db: Session = Depends(get_db)) -> dict[str, int]:
    rows = (
        db.query(GiftCommitment.gift_item_id, func.sum(GiftCommitment.quantity))
        .group_by(GiftCommitment.gift_item_id)
        .all()
    )
    return {gift_item_id: int(total) for gift_item_id, total in rows}
