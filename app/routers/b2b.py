from fastapi import APIRouter, Header, HTTPException, status
from sqlalchemy import select

from app.config import settings
from app.dependencies import DB, CurrentUser
from app.models.b2b import B2BProfile, PriceGroup, PriceGroupMember, PriceGroupProduct
from app.models.product import Product
from app.models.user import User
from app.schemas.b2b import B2BVerificationRequest, B2BVerificationStatus, PriceGroupOut, PriceGroupProductOut

router = APIRouter()


@router.post("/verification", status_code=status.HTTP_201_CREATED)
async def submit_verification(body: B2BVerificationRequest, user: CurrentUser, db: DB):
    existing = await db.execute(select(B2BProfile).where(B2BProfile.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Verification already submitted")

    profile = B2BProfile(
        user_id=user.id,
        business_name=body.business_name or "",
        business_type=body.business_type or "",
        ip_number=body.ip_number,
        document_url=body.document_url,
        shop_photo_url=body.shop_photo_url,
        verification_status="submitted",
        lat=body.location.lat if body.location else None,
        lon=body.location.lon if body.location else None,
    )
    db.add(profile)
    await db.commit()
    return {"success": True}


@router.get("/verification/status", response_model=B2BVerificationStatus)
async def get_verification_status(user: CurrentUser, db: DB):
    result = await db.execute(select(B2BProfile).where(B2BProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        return B2BVerificationStatus(status="none")
    return B2BVerificationStatus(status=profile.verification_status)


@router.put("/verification/{user_id}/approve")
async def approve_verification(
    user_id: int,
    db: DB,
    x_admin_secret: str = Header(alias="X-Admin-Secret"),
):
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    result = await db.execute(select(B2BProfile).where(B2BProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Verification not found")

    profile.verification_status = "verified"

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "b2b"
    await db.commit()
    return {"success": True, "userId": user_id, "role": "b2b"}


@router.get("/price-groups", response_model=list[PriceGroupOut])
async def get_price_groups(user: CurrentUser, db: DB):
    memberships = await db.execute(
        select(PriceGroupMember.price_group_id).where(PriceGroupMember.user_id == user.id)
    )
    group_ids = [m for m in memberships.scalars().all()]

    if not group_ids:
        result = await db.execute(select(PriceGroup))
    else:
        result = await db.execute(select(PriceGroup).where(PriceGroup.id.in_(group_ids)))

    groups = result.scalars().all()
    out = []
    for g in groups:
        pg_products = await db.execute(
            select(PriceGroupProduct).where(PriceGroupProduct.price_group_id == g.id)
        )
        products_out = []
        for pgp in pg_products.scalars().all():
            prod = await db.execute(select(Product).where(Product.id == pgp.product_id))
            product = prod.scalar_one_or_none()
            if product:
                products_out.append(PriceGroupProductOut(
                    name=product.name, regular_price=product.price,
                    group_price=pgp.special_price, unit=product.unit,
                ))
        out.append(PriceGroupOut(
            id=g.id, name=g.name, discount=g.discount_percent,
            description=g.description, products=products_out,
        ))
    return out
