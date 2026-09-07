from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import AdminUser, GiftCommitment, GiftItem
from ..schemas import PersonGiftOut

router = APIRouter(prefix="/api/lista-pessoas", tags=["lista-pessoas"])


@router.get("", response_model=list[PersonGiftOut])
def list_people(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> list[PersonGiftOut]:
    rows = (
        db.query(GiftCommitment, GiftItem)
        .join(GiftItem, GiftCommitment.gift_item_id == GiftItem.id)
        .order_by(GiftCommitment.guest_name, GiftCommitment.created_at)
        .all()
    )
    return [
        PersonGiftOut(
            guest_name=commitment.guest_name or "Não identificado",
            item_name=item.name,
            item_size=item.size,
            quantity=commitment.quantity,
            created_at=commitment.created_at,
        )
        for commitment, item in rows
    ]
