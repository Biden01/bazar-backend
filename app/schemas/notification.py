from datetime import datetime

from app.schemas.base import CamelModel


class NotificationOut(CamelModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
