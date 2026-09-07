from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, require_admin, verify_password
from ..database import get_db
from ..models import AdminUser
from ..schemas import (
    AdminLogin,
    AdminMe,
    AdminRegister,
    AdminUserCreate,
    AdminUserOut,
    AdminUserRoleUpdate,
    TokenResponse,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _new_user(db: Session, email: str, username: str | None, password: str, is_admin: bool) -> AdminUser:
    email = email.strip().lower()
    if db.query(AdminUser).filter(AdminUser.email == email).first():
        raise HTTPException(status_code=400, detail="Este e-mail já tem uma conta.")

    username = username.strip().lower() if username else None
    if username and db.query(AdminUser).filter(AdminUser.username == username).first():
        raise HTTPException(status_code=400, detail="Este nome de usuário já está em uso.")

    user = AdminUser(
        email=email,
        username=username,
        password_hash=hash_password(password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AdminRegister, db: Session = Depends(get_db)) -> TokenResponse:
    is_first_admin = db.query(AdminUser).count() == 0
    user = _new_user(db, payload.email, payload.username, payload.password, is_first_admin)

    return TokenResponse(
        access_token=create_access_token(user),
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLogin, db: Session = Depends(get_db)) -> TokenResponse:
    identifier = payload.identifier.strip().lower()
    user = (
        db.query(AdminUser)
        .filter(or_(AdminUser.email == identifier, AdminUser.username == identifier))
        .first()
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail/usuário ou senha não conferem.")

    return TokenResponse(
        access_token=create_access_token(user),
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
    )


@router.get("/me", response_model=AdminMe)
def me(user: AdminUser = Depends(get_current_user)) -> AdminMe:
    return AdminMe(id=user.id, email=user.email, username=user.username, is_admin=user.is_admin)


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    db: Session = Depends(get_db), _: AdminUser = Depends(require_admin)
) -> list[AdminUser]:
    return db.query(AdminUser).order_by(AdminUser.created_at.asc()).all()


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(require_admin),
) -> AdminUser:
    return _new_user(db, payload.email, payload.username, payload.password, payload.is_admin)


@router.patch("/users/{user_id}/role", response_model=AdminUserOut)
def update_user_role(
    user_id: str,
    payload: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    current: AdminUser = Depends(require_admin),
) -> AdminUser:
    target = db.get(AdminUser, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if target.id == current.id and not payload.is_admin:
        raise HTTPException(
            status_code=400, detail="Você não pode remover sua própria permissão de admin."
        )

    target.is_admin = payload.is_admin
    db.commit()
    db.refresh(target)
    return target
