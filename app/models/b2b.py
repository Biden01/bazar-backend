from sqlalchemy import String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class B2BProfile(Base):
    __tablename__ = "b2b_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    business_name: Mapped[str] = mapped_column(String(200))
    business_type: Mapped[str] = mapped_column(String(50))
    ip_number: Mapped[str] = mapped_column(String(50))
    verification_status: Mapped[str] = mapped_column(String(20), default="pending")
    document_url: Mapped[str | None] = mapped_column(String(500))
    shop_photo_url: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)


class PriceGroup(Base):
    __tablename__ = "price_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)


class PriceGroupMember(Base):
    __tablename__ = "price_group_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    price_group_id: Mapped[int] = mapped_column(ForeignKey("price_groups.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)


class PriceGroupProduct(Base):
    __tablename__ = "price_group_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    price_group_id: Mapped[int] = mapped_column(ForeignKey("price_groups.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    special_price: Mapped[int] = mapped_column(Integer)
