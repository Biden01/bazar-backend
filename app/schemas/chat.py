from datetime import datetime

from app.schemas.base import CamelModel


class MessageOut(CamelModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    created_at: datetime
    is_mine: bool = False


class MessageCreate(CamelModel):
    text: str


class ChatOut(CamelModel):
    id: int
    buyer_id: int
    seller_id: int
    last_message_at: datetime | None = None
    other_user_name: str | None = None
    last_message_text: str | None = None
