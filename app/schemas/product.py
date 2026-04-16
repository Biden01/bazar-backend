from app.schemas.base import CamelModel


class ProductImageOut(CamelModel):
    id: int
    url: str
    sort_order: int


class ProductOut(CamelModel):
    id: int
    name: str
    category: str
    price: int
    wholesale_price: int | None = None
    unit: str
    stock: int
    min_order: int
    description: str | None = None
    rating: float
    review_count: int
    is_active: bool
    seller_id: int
    seller_name: str | None = None
    images: list[ProductImageOut] = []


class ProductCreate(CamelModel):
    name: str
    category: str
    price: int
    wholesale_price: int | None = None
    unit: str
    stock: int = 0
    min_order: int = 1
    description: str | None = None
    image_ids: list[int] = []


class ProductUpdate(CamelModel):
    name: str | None = None
    category: str | None = None
    price: int | None = None
    wholesale_price: int | None = None
    unit: str | None = None
    stock: int | None = None
    min_order: int | None = None
    description: str | None = None


class ProductListResponse(CamelModel):
    items: list[ProductOut]
    total: int
    page: int
