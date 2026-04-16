from app.schemas.base import CamelModel


class UserOut(CamelModel):
    id: int
    phone: str
    name: str | None = None
    role: str
    avatar_url: str | None = None
    location: str | None = None


class UserUpdate(CamelModel):
    name: str | None = None
    avatar_url: str | None = None
    location: str | None = None
