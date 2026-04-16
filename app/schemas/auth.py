from pydantic import BaseModel

from app.schemas.base import CamelModel


class SendOTPRequest(BaseModel):
    phone: str


class SendOTPResponse(CamelModel):
    success: bool = True
    expires_in: int = 120


class VerifyOTPRequest(BaseModel):
    phone: str
    code: str


class UserBrief(CamelModel):
    id: int
    phone: str
    role: str


class VerifyOTPResponse(CamelModel):
    access_token: str
    refresh_token: str
    user: UserBrief


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(CamelModel):
    access_token: str
    refresh_token: str


class RoleRequest(BaseModel):
    role: str


class SuccessResponse(CamelModel):
    success: bool = True
