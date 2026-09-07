from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CategoryOut(BaseModel):
    id: str
    name: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class GiftItemOut(BaseModel):
    id: str
    category_id: str
    name: str
    size: Optional[str] = None
    description: Optional[str] = None
    desired_quantity: int
    active: bool
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class GiftItemCreate(BaseModel):
    category_id: str
    name: str = Field(min_length=1, max_length=255)
    size: Optional[str] = None
    description: Optional[str] = None
    desired_quantity: int = Field(default=1, ge=1, le=99)
    display_order: int = 0


class GiftItemUpdate(BaseModel):
    category_id: Optional[str] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    size: Optional[str] = None
    description: Optional[str] = None
    desired_quantity: Optional[int] = Field(default=None, ge=1, le=99)
    active: Optional[bool] = None
    display_order: Optional[int] = None


class GiftCommitmentOut(BaseModel):
    id: str
    gift_item_id: str
    guest_name: Optional[str] = None
    quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GiftCommitmentCreate(BaseModel):
    gift_item_id: str
    guest_name: str = ""
    quantity: int = Field(default=1, ge=1, le=99)


class GiftCommitmentBulkItem(BaseModel):
    gift_item_id: str
    quantity: int = Field(default=1, ge=1, le=99)


class GiftCommitmentBulkCreate(BaseModel):
    guest_name: str = ""
    items: list[GiftCommitmentBulkItem] = Field(min_length=1, max_length=50)


class AdminRegister(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(default=None, min_length=3, max_length=40)
    password: str = Field(min_length=6, max_length=72)


class AdminLogin(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    username: Optional[str] = None
    is_admin: bool


class AdminMe(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    is_admin: bool


class AdminUserOut(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserRoleUpdate(BaseModel):
    is_admin: bool


class AdminUserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(default=None, min_length=3, max_length=40)
    password: str = Field(min_length=6, max_length=72)
    is_admin: bool = False


class PersonGiftOut(BaseModel):
    guest_name: str
    item_name: str
    item_size: Optional[str] = None
    quantity: int
    created_at: datetime
