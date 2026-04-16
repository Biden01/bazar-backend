import json
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI

from app.config import settings
from app.dependencies import CurrentUser

router = APIRouter()


def _client() -> AsyncOpenAI:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="AI сервис не настроен")
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# ─── /ai/chat ────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class AIChatContext(BaseModel):
    userRole: str = "buyer"
    currentProducts: list[dict] | None = None

class AIChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: AIChatContext | None = None

class AIChatResponse(BaseModel):
    message: str
    cartItems: list[dict] | None = None


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(body: AIChatRequest, user: CurrentUser):
    client = _client()

    context = body.context
    role_label = "продавец на базаре" if context and context.userRole == "seller" else "покупатель"
    products_info = ""
    if context and context.currentProducts:
        items = ", ".join(
            f"{p['name']} {p['price']}₸/{p['unit']}"
            for p in context.currentProducts[:20]
        )
        products_info = f"\nДоступные товары: {items}"

    system_prompt = (
        f"Ты помощник в приложении Bazar Digital — казахстанский торговый маркетплейс города Тараз. "
        f"Пользователь: {role_label}.{products_info}\n"
        "Отвечай кратко и по делу на русском языке. "
        "Если покупатель хочет добавить товары в корзину, верни JSON в поле cartItems."
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *[{"role": m.role, "content": m.content} for m in body.messages],
        ],
        max_tokens=500,
        temperature=0.7,
    )

    content = response.choices[0].message.content or ""

    # Попробуем извлечь cartItems если GPT вернул JSON
    cart_items = None
    try:
        if "cartItems" in content:
            start = content.index("{")
            end = content.rindex("}") + 1
            data = json.loads(content[start:end])
            cart_items = data.get("cartItems")
            content = content[:start].strip() or content
    except Exception:
        pass

    return AIChatResponse(message=content, cartItems=cart_items)


# ─── /ai/parse-voice ─────────────────────────────────────────────────────────

class VoiceParseRequest(BaseModel):
    text: str

class ParsedSale(BaseModel):
    product: str
    quantity: float
    unit: str
    price: float
    paymentMethod: Literal["cash", "kaspi", "debt"]
    buyerName: str | None = None
    total: float

class VoiceParseResponse(BaseModel):
    parsed: ParsedSale


@router.post("/parse-voice", response_model=VoiceParseResponse)
async def parse_voice(body: VoiceParseRequest, user: CurrentUser):
    client = _client()

    system_prompt = (
        "Ты парсер голосовых команд для торговцев на базаре. "
        "Извлеки из текста данные о продаже и верни ТОЛЬКО валидный JSON без markdown:\n"
        '{"product": "название товара", "quantity": число, "unit": "кг|г|шт|л|мешок|ящик|пачка", '
        '"price": цена_за_единицу, "paymentMethod": "cash|kaspi|debt", '
        '"buyerName": "имя или null", "total": quantity*price}\n'
        "paymentMethod: cash=наличные/налом, kaspi=kaspi/картой, debt=долг/потом/в долг"
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body.text},
        ],
        max_tokens=200,
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
        parsed = ParsedSale(
            product=data.get("product", "Товар"),
            quantity=float(data.get("quantity", 1)),
            unit=data.get("unit", "кг"),
            price=float(data.get("price", 0)),
            paymentMethod=data.get("paymentMethod", "cash"),
            buyerName=data.get("buyerName") or None,
            total=float(data.get("total", 0)),
        )
    except Exception:
        raise HTTPException(status_code=422, detail="Не удалось распознать текст")

    return VoiceParseResponse(parsed=parsed)
