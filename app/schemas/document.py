from datetime import date

from app.schemas.base import CamelModel


class VetCertOut(CamelModel):
    id: int
    number: str
    product: str
    issue_date: date
    expiry_date: date
    issuer: str
    status: str
    seller_name: str | None = None


class VetCertCreate(CamelModel):
    number: str
    product: str
    issue_date: date
    expiry_date: date
    issuer: str
    status: str = "valid"
    document_url: str | None = None


class InvoiceOut(CamelModel):
    id: int
    number: str
    date: date
    seller_name: str | None = None
    buyer_name: str | None = None
    amount: int
    items: int
    status: str
