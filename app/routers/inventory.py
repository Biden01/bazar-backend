from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import DB, SellerUser
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryOut, InventoryCreate, InventoryUpdate

router = APIRouter()


@router.get("", response_model=list[InventoryOut])
async def list_inventory(user: SellerUser, db: DB):
    result = await db.execute(
        select(Inventory).where(Inventory.seller_id == user.id).order_by(Inventory.updated_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
async def create_inventory(body: InventoryCreate, user: SellerUser, db: DB):
    item = Inventory(seller_id=user.id, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=InventoryOut)
async def update_inventory(item_id: int, body: InventoryUpdate, user: SellerUser, db: DB):
    result = await db.execute(select(Inventory).where(Inventory.id == item_id, Inventory.seller_id == user.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_inventory(item_id: int, user: SellerUser, db: DB):
    result = await db.execute(select(Inventory).where(Inventory.id == item_id, Inventory.seller_id == user.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()
    return {"success": True}
