from app.schemas.base import CamelModel


class CalculatorItem(CamelModel):
    name: str
    unit: str
    quantity: float
    price_from: int
    total: int
    image: str


class CalculatorResponse(CamelModel):
    guests: int
    event_type: str
    items: list[CalculatorItem]
    grand_total: int
