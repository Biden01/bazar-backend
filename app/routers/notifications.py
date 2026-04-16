from fastapi import APIRouter
from sqlalchemy import select, update

from app.dependencies import DB, CurrentUser
from app.models.notification import Notification
from app.schemas.notification import NotificationOut

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
async def list_notifications(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.put("/read-all")
async def mark_all_read(user: CurrentUser, db: DB):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"success": True}
