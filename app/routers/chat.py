import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select, or_, and_, desc

from app.dependencies import DB, CurrentUser, get_db
from app.models.chat import Chat, Message
from app.models.user import User
from app.schemas.chat import ChatOut, MessageOut, MessageCreate
from app.services.jwt import decode_token

router = APIRouter()

# Simple in-memory connection manager
active_connections: dict[int, list[WebSocket]] = {}


@router.get("", response_model=list[ChatOut])
async def list_chats(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Chat)
        .where(or_(Chat.buyer_id == user.id, Chat.seller_id == user.id))
        .order_by(desc(Chat.last_message_at))
    )
    chats = result.scalars().all()

    out = []
    for c in chats:
        await db.refresh(c, ["buyer", "seller", "messages"])
        other = c.seller if c.buyer_id == user.id else c.buyer
        last_msg = c.messages[-1].text if c.messages else None
        out.append(ChatOut(
            id=c.id, buyer_id=c.buyer_id, seller_id=c.seller_id,
            last_message_at=c.last_message_at,
            other_user_name=other.name if other else None,
            last_message_text=last_msg,
        ))
    return out


@router.get("/{seller_id}/messages", response_model=list[MessageOut])
async def get_messages(
    seller_id: int, user: CurrentUser, db: DB,
    before: int | None = None,
    limit: int = Query(50, ge=1, le=100),
):
    chat = await _get_or_create_chat(user.id, seller_id, db)

    query = select(Message).where(Message.chat_id == chat.id)
    if before:
        query = query.where(Message.id < before)
    query = query.order_by(desc(Message.id)).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        MessageOut(
            id=m.id, chat_id=m.chat_id, sender_id=m.sender_id,
            text=m.text, created_at=m.created_at, is_mine=(m.sender_id == user.id),
        )
        for m in reversed(messages)
    ]


@router.post("/{seller_id}/messages", response_model=MessageOut)
async def send_message(seller_id: int, body: MessageCreate, user: CurrentUser, db: DB):
    chat = await _get_or_create_chat(user.id, seller_id, db)

    msg = Message(chat_id=chat.id, sender_id=user.id, text=body.text)
    db.add(msg)
    chat.last_message_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)

    # Notify connected WebSocket clients
    other_id = chat.seller_id if chat.buyer_id == user.id else chat.buyer_id
    if other_id in active_connections:
        data = json.dumps({"chat_id": chat.id, "message_id": msg.id, "text": msg.text, "sender_id": user.id})
        for ws in active_connections[other_id]:
            try:
                await ws.send_text(data)
            except Exception:
                pass

    return MessageOut(
        id=msg.id, chat_id=msg.chat_id, sender_id=msg.sender_id,
        text=msg.text, created_at=msg.created_at, is_mine=True,
    )


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = int(payload["sub"])
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]


async def _get_or_create_chat(user_id: int, seller_id: int, db) -> Chat:
    result = await db.execute(
        select(Chat).where(
            or_(
                and_(Chat.buyer_id == user_id, Chat.seller_id == seller_id),
                and_(Chat.buyer_id == seller_id, Chat.seller_id == user_id),
            )
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        chat = Chat(buyer_id=user_id, seller_id=seller_id)
        db.add(chat)
        await db.flush()
    return chat
