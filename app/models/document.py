from datetime import date, datetime

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VetCert(Base):
    __tablename__ = "vet_certs"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    number: Mapped[str] = mapped_column(String(50))
    product: Mapped[str] = mapped_column(String(200))
    issue_date: Mapped[date] = mapped_column(Date)
    expiry_date: Mapped[date] = mapped_column(Date)
    issuer: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))
    document_url: Mapped[str | None] = mapped_column(String(500))


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    number: Mapped[str] = mapped_column(String(50))
    date: Mapped[date] = mapped_column(Date)
    amount: Mapped[int] = mapped_column(Integer)
    item_count: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
