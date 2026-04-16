from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.dependencies import DB, SellerUser
from app.models.debt import Debt, DebtPayment
from app.schemas.debt import DebtOut, DebtCreate, DebtUpdate, DebtPaymentCreate, DebtListResponse

router = APIRouter()


@router.get("", response_model=DebtListResponse)
async def list_debts(user: SellerUser, db: DB, status_filter: str | None = Query(None, alias="status")):
    query = select(Debt).where(Debt.seller_id == user.id)
    if status_filter:
        query = query.where(Debt.status == status_filter)
    query = query.order_by(Debt.created_at.desc())
    result = await db.execute(query)
    debts = result.scalars().all()

    for d in debts:
        await db.refresh(d, ["payments"])

    total = sum(d.amount for d in debts)
    paid = sum(d.paid_amount for d in debts)
    return DebtListResponse(
        items=debts,
        totals={"total": total, "paid": paid, "remaining": total - paid},
    )


@router.post("", response_model=DebtOut, status_code=status.HTTP_201_CREATED)
async def create_debt(body: DebtCreate, user: SellerUser, db: DB):
    debt = Debt(seller_id=user.id, **body.model_dump())
    db.add(debt)
    await db.commit()
    await db.refresh(debt, ["payments"])
    return debt


@router.put("/{debt_id}", response_model=DebtOut)
async def update_debt(debt_id: int, body: DebtUpdate, user: SellerUser, db: DB):
    result = await db.execute(select(Debt).where(Debt.id == debt_id, Debt.seller_id == user.id))
    debt = result.scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(debt, field, value)
    await db.commit()
    await db.refresh(debt, ["payments"])
    return debt


@router.delete("/{debt_id}")
async def delete_debt(debt_id: int, user: SellerUser, db: DB):
    result = await db.execute(select(Debt).where(Debt.id == debt_id, Debt.seller_id == user.id))
    debt = result.scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    await db.delete(debt)
    await db.commit()
    return {"success": True}


@router.post("/{debt_id}/payment", response_model=DebtOut)
async def add_payment(debt_id: int, body: DebtPaymentCreate, user: SellerUser, db: DB):
    result = await db.execute(select(Debt).where(Debt.id == debt_id, Debt.seller_id == user.id))
    debt = result.scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    payment = DebtPayment(debt_id=debt.id, amount=body.amount)
    db.add(payment)

    debt.paid_amount += body.amount
    if debt.paid_amount >= debt.amount:
        debt.status = "paid"
    elif debt.paid_amount > 0:
        debt.status = "partial"

    await db.commit()
    await db.refresh(debt, ["payments"])
    return debt
