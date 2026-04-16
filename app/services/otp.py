import random

from fastapi import HTTPException, status

from app.config import settings
from app.utils.redis import redis_client

OTP_TTL = 120  # seconds


async def send_otp(phone: str) -> str:
    attempts_key = f"otp_attempts:{phone}"
    attempts = await redis_client.get(attempts_key)
    if attempts and int(attempts) >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Try again in 10 minutes.",
        )

    pipe = redis_client.pipeline()
    pipe.incr(attempts_key)
    pipe.expire(attempts_key, settings.OTP_ATTEMPTS_WINDOW)
    await pipe.execute()

    if settings.DEV_MODE:
        code = "1234"
    else:
        code = f"{random.randint(1000, 9999)}"

    await redis_client.set(f"otp:{phone}", code, ex=OTP_TTL)
    return code


async def verify_otp(phone: str, code: str) -> bool:
    if settings.DEV_MODE:
        return True
    stored = await redis_client.get(f"otp:{phone}")
    if stored and stored == code:
        await redis_client.delete(f"otp:{phone}")
        await redis_client.delete(f"otp_attempts:{phone}")
        return True
    return False
