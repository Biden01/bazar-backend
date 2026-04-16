from datetime import datetime

from app.schemas.base import CamelModel


class InventoryOut(CamelModel):
    id: int
    name: str
    category: str
    price: int
    unit: str
    stock: int
    min_stock: int
    is_public: bool
    is_active: bool
    image_url: str | None = None
    updated_at: datetime | None = None


class InventoryCreate(CamelModel):
    name: str
    category: str
    price: int
    unit: str
    stock: int = 0
    min_stock: int = 0
    is_public: bool = True
    is_active: bool = True
    image_url: str | None = None


class InventoryUpdate(CamelModel):
    name: str | None = None
    category: str | None = None
    price: int | None = None
    unit: str | None = None
    stock: int | None = None
    min_stock: int | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    image_url: str | None = None
