import re

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.dependencies import DB, CurrentUser
from app.limiter import limiter
from app.models.user import User
from app.schemas.auth import (
    SendOTPRequest, SendOTPResponse,
    VerifyOTPRequest, VerifyOTPResponse, UserBrief,
    RefreshRequest, RefreshResponse,
    RoleRequest, SuccessResponse,
)
from app.services.jwt import create_access_token, create_refresh_token, decode_token
from app.services.otp import send_otp, verify_otp
from app.config import settings

router = APIRouter()

PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def _validate_phone(phone: str):
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid phone number format")


@router.post("/send-otp", response_model=SendOTPResponse)
@limiter.limit(settings.OTP_RATE_LIMIT)
async def send_otp_endpoint(request: Request, body: SendOTPRequest):
    _validate_phone(body.phone)
    await send_otp(body.phone)
    return SendOTPResponse()


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp_endpoint(body: VerifyOTPRequest, db: DB):
    _validate_phone(body.phone)
    valid = await verify_otp(body.phone, body.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    if not user:
        user = User(phone=body.phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access = create_access_token(user.id, user.role)
    refresh = create_refresh_token(user.id)
    return VerifyOTPResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserBrief(id=user.id, phone=user.phone, role=user.role),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_endpoint(body: RefreshRequest, db: DB):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(user.id, user.role)
    refresh = create_refresh_token(user.id)
    return RefreshResponse(access_token=access, refresh_token=refresh)


@router.put("/role", response_model=SuccessResponse)
async def update_role(body: RoleRequest, user: CurrentUser, db: DB):
    if body.role not in ("buyer", "seller", "b2b"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    user.role = body.role
    await db.commit()
    return SuccessResponse()
