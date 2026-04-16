from fastapi import APIRouter

from app.dependencies import DB, CurrentUser
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser):
    return user


@router.put("/me", response_model=UserOut)
async def update_me(body: UserUpdate, user: CurrentUser, db: DB):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user
