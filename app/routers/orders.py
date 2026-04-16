from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.dependencies import DB, CurrentUser, SellerUser
from app.models.order import Order, OrderItem, Review
from app.models.product import Product
from app.schemas.order import (
    OrderCreate, OrderCreateResponse, OrderOut, OrderItemOut,
    OrderStatusUpdate, ReviewCreate, ReviewOut,
)

router = APIRouter()

VALID_TRANSITIONS = {
    "new": ["confirmed", "cancelled"],
    "confirmed": ["assembling", "cancelled"],
    "assembling": ["ready", "cancelled"],
    "ready": ["completed", "cancelled"],
}


@router.post("", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(body: OrderCreate, user: CurrentUser, db: DB):
    if not body.items:
        raise HTTPException(status_code=400, detail="No items")

    # Load first product to determine seller
    first = await db.execute(select(Product).where(Product.id == body.items[0].product_id))
    first_product = first.scalar_one_or_none()
    if not first_product:
        raise HTTPException(status_code=400, detail="Product not found")

    seller_id = first_product.seller_id
    total = 0
    order_items = []

    for item in body.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id, Product.is_active == True))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        price = product.wholesale_price or product.price
        product.stock -= item.quantity
        total += price * item.quantity
        order_items.append(OrderItem(product_id=product.id, quantity=item.quantity, price=price))

    order = Order(
        buyer_id=user.id, seller_id=seller_id, status="new",
        delivery_type=body.delivery_type, payment_method=body.payment_method,
        address=body.address, total=total, items=order_items,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return OrderCreateResponse(order_id=order.id, status=order.status)


@router.get("", response_model=list[OrderOut])
async def list_orders(
    user: CurrentUser, db: DB,
    status_filter: str | None = Query(None, alias="status"),
    role: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    if role == "seller":
        query = select(Order).where(Order.seller_id == user.id)
    else:
        query = select(Order).where(Order.buyer_id == user.id)

    if status_filter:
        query = query.where(Order.status == status_filter)

    query = query.order_by(Order.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()

    out = []
    for o in orders:
        await db.refresh(o, ["items", "buyer", "seller"])
        items_out = []
        for oi in o.items:
            await db.refresh(oi, ["product"])
            items_out.append(OrderItemOut(
                id=oi.id, product_id=oi.product_id, quantity=oi.quantity,
                price=oi.price, product_name=oi.product.name if oi.product else None,
            ))
        out.append(OrderOut(
            id=o.id, buyer_id=o.buyer_id, seller_id=o.seller_id,
            status=o.status, delivery_type=o.delivery_type,
            payment_method=o.payment_method, address=o.address,
            total=o.total, created_at=o.created_at, items=items_out,
            buyer_name=o.buyer.name if o.buyer else None,
            seller_name=o.seller.name if o.seller else None,
        ))
    return out


@router.put("/{order_id}/status")
async def update_order_status(order_id: int, body: OrderStatusUpdate, user: SellerUser, db: DB):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.seller_id == user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Cannot transition from {order.status} to {body.status}")

    if body.status == "cancelled":
        await db.refresh(order, ["items"])
        for oi in order.items:
            result = await db.execute(select(Product).where(Product.id == oi.product_id))
            product = result.scalar_one_or_none()
            if product:
                product.stock += oi.quantity

    order.status = body.status
    await db.commit()
    return {"success": True, "status": order.status}


@router.post("/{order_id}/review", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(order_id: int, body: ReviewCreate, user: CurrentUser, db: DB):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.buyer_id == user.id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing = await db.execute(select(Review).where(Review.order_id == order_id, Review.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already reviewed")

    review = Review(order_id=order_id, user_id=user.id, rating=body.rating, comment=body.comment)
    db.add(review)

    # Update product ratings for all items in the order
    await db.refresh(order, ["items"])
    for oi in order.items:
        result = await db.execute(select(Product).where(Product.id == oi.product_id))
        product = result.scalar_one_or_none()
        if product:
            total_rating = product.rating * product.review_count + body.rating
            product.review_count += 1
            product.rating = round(total_rating / product.review_count, 1)

    await db.commit()
    await db.refresh(review)
    return ReviewOut(
        id=review.id, order_id=review.order_id, user_id=review.user_id,
        rating=review.rating, comment=review.comment, created_at=review.created_at,
        user_name=user.name,
    )
