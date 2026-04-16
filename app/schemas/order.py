from datetime import datetime

from app.schemas.base import CamelModel


class OrderItemCreate(CamelModel):
    product_id: int
    quantity: int


class OrderCreate(CamelModel):
    items: list[OrderItemCreate]
    delivery_type: str
    payment_method: str
    address: str | None = None


class OrderCreateResponse(CamelModel):
    order_id: int
    status: str


class OrderItemOut(CamelModel):
    id: int
    product_id: int
    quantity: int
    price: int
    product_name: str | None = None


class OrderOut(CamelModel):
    id: int
    buyer_id: int
    seller_id: int
    status: str
    delivery_type: str
    payment_method: str
    address: str | None = None
    total: int
    created_at: datetime
    items: list[OrderItemOut] = []
    buyer_name: str | None = None
    seller_name: str | None = None


class OrderStatusUpdate(CamelModel):
    status: str


class ReviewCreate(CamelModel):
    rating: int
    comment: str | None = None


class ReviewOut(CamelModel):
    id: int
    order_id: int
    user_id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    user_name: str | None = None
