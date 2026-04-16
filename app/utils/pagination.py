from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(db: AsyncSession, query, page: int = 1, limit: int = 20):
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * limit
    items_q = query.offset(offset).limit(limit)
    result = await db.execute(items_q)
    items = result.scalars().all()

    return {"items": items, "total": total, "page": page}
