import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship

from .database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(60), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    items = relationship("GiftItem", back_populates="category", cascade="all, delete-orphan")


class GiftItem(Base):
    __tablename__ = "gift_items"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    size = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    desired_quantity = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", back_populates="items")
    commitments = relationship("GiftCommitment", back_populates="item", cascade="all, delete-orphan")


class GiftCommitment(Base):
    __tablename__ = "gift_commitments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    gift_item_id = Column(
        String(36), ForeignKey("gift_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    guest_name = Column(String(60), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    item = relationship("GiftItem", back_populates="commitments")
