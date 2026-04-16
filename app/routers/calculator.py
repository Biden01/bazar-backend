import math

from fastapi import APIRouter, Query
from sqlalchemy import select, func

from app.dependencies import DB
from app.models.product import Product
from app.schemas.calculator import CalculatorResponse, CalculatorItem

router = APIRouter()

PER_PERSON = {
    "Той": {"beef": 0.5, "lamb": 0.3, "potato": 0.4, "onion": 0.2, "carrot": 0.15, "drinks": 0.4},
    "День рождения": {"beef": 0.4, "lamb": 0.2, "potato": 0.3, "onion": 0.15, "carrot": 0.1, "drinks": 0.5},
    "Поминки": {"beef": 0.6, "lamb": 0.4, "potato": 0.5, "onion": 0.25, "carrot": 0.2, "drinks": 0.2},
    "Другое": {"beef": 0.3, "lamb": 0.2, "potato": 0.3, "onion": 0.15, "carrot": 0.1, "drinks": 0.3},
}

PRODUCT_MAP = {
    "beef": {"name": "Говядина (вырезка)", "unit": "кг", "image": "🥩", "search": "Говядина"},
    "lamb": {"name": "Баранина", "unit": "кг", "image": "🍖", "search": "Баранина"},
    "potato": {"name": "Картофель", "unit": "кг", "image": "🥔", "search": "Картофель"},
    "onion": {"name": "Лук", "unit": "кг", "image": "🧅", "search": "Лук"},
    "carrot": {"name": "Морковь", "unit": "кг", "image": "🥕", "search": "Морковь"},
    "drinks": {"name": "Напитки 1.5л", "unit": "шт", "image": "🥤", "search": "Напитки"},
}


@router.get("/estimate", response_model=CalculatorResponse)
async def estimate(
    db: DB,
    guests: int = Query(50, ge=1),
    event_type: str = Query("Той"),
):
    ratios = PER_PERSON.get(event_type, PER_PERSON["Другое"])
    items = []
    grand_total = 0

    for key, ratio in ratios.items():
        info = PRODUCT_MAP[key]
        quantity = math.ceil(guests * ratio)

        # Find best price from DB
        result = await db.execute(
            select(func.min(Product.price))
            .where(Product.is_active == True, Product.name.ilike(f"%{info['search']}%"))
        )
        best_price = result.scalar() or 0
        total = best_price * quantity
        grand_total += total

        items.append(CalculatorItem(
            name=info["name"], unit=info["unit"], quantity=quantity,
            price_from=best_price, total=total, image=info["image"],
        ))

    return CalculatorResponse(
        guests=guests, event_type=event_type, items=items, grand_total=grand_total,
    )
