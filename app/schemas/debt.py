from datetime import date, datetime

from app.schemas.base import CamelModel


class DebtPaymentOut(CamelModel):
    id: int
    amount: int
    date: date


class DebtOut(CamelModel):
    id: int
    buyer_name: str
    amount: int
    paid_amount: int
    status: str
    description: str | None = None
    due_date: date
    created_at: datetime
    payments: list[DebtPaymentOut] = []


class DebtCreate(CamelModel):
    buyer_name: str
    amount: int
    description: str | None = None
    due_date: date


class DebtUpdate(CamelModel):
    buyer_name: str | None = None
    amount: int | None = None
    description: str | None = None
    due_date: date | None = None


class DebtPaymentCreate(CamelModel):
    amount: int


class DebtListResponse(CamelModel):
    items: list[DebtOut]
    totals: dict
