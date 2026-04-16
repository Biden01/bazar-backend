from datetime import datetime

from app.schemas.base import CamelModel


class LocationIn(CamelModel):
    lat: float
    lon: float


class B2BVerificationRequest(CamelModel):
    ip_number: str
    business_name: str | None = None
    business_type: str | None = None
    document_url: str | None = None
    shop_photo_url: str | None = None
    location: LocationIn | None = None


class B2BVerificationStatus(CamelModel):
    status: str
    submitted_at: datetime | None = None
    verified_at: datetime | None = None


class PriceGroupProductOut(CamelModel):
    name: str
    regular_price: int
    group_price: int
    unit: str


class PriceGroupOut(CamelModel):
    id: int
    name: str
    discount: int
    description: str | None = None
    products: list[PriceGroupProductOut] = []
