from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, or_, func

from app.dependencies import DB, CurrentUser, SellerUser
from app.models.product import Product, ProductImage
from app.models.user import User
from app.schemas.product import ProductOut, ProductCreate, ProductUpdate, ProductListResponse
from app.utils.pagination import paginate

router = APIRouter()


def _product_to_out(p: Product) -> ProductOut:
    return ProductOut(
        id=p.id, name=p.name, category=p.category, price=p.price,
        wholesale_price=p.wholesale_price, unit=p.unit, stock=p.stock,
        min_order=p.min_order, description=p.description, rating=p.rating,
        review_count=p.review_count, is_active=p.is_active, seller_id=p.seller_id,
        seller_name=p.seller.name if p.seller else None,
        images=[{"id": img.id, "url": img.url, "sort_order": img.sort_order} for img in p.images],
    )


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: DB,
    category: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    seller_id: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = select(Product).where(Product.is_active == True)

    if category:
        query = query.where(Product.category == category)
    if seller_id:
        query = query.where(Product.seller_id == seller_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )

    if sort == "price":
        query = query.order_by(Product.price.asc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    result = await paginate(db, query, page, limit)

    # Eager load relationships
    products = result["items"]
    items = []
    for p in products:
        await db.refresh(p, ["seller", "images"])
        items.append(_product_to_out(p))

    return ProductListResponse(items=items, total=result["total"], page=result["page"])


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: DB):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.refresh(product, ["seller", "images"])
    return _product_to_out(product)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, user: SellerUser, db: DB):
    product = Product(
        seller_id=user.id,
        name=body.name, category=body.category, price=body.price,
        wholesale_price=body.wholesale_price, unit=body.unit,
        stock=body.stock, min_order=body.min_order, description=body.description,
    )
    db.add(product)
    await db.flush()

    for img_id in body.image_ids:
        result = await db.execute(select(ProductImage).where(ProductImage.id == img_id))
        img = result.scalar_one_or_none()
        if img:
            img.product_id = product.id

    await db.commit()
    await db.refresh(product, ["seller", "images"])
    return _product_to_out(product)


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, body: ProductUpdate, user: SellerUser, db: DB):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.seller_id == user.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product, ["seller", "images"])
    return _product_to_out(product)


@router.delete("/{product_id}")
async def delete_product(product_id: int, user: SellerUser, db: DB):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.seller_id == user.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    await db.commit()
    return {"success": True}
