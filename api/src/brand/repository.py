"""Database access for brands."""

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from enums import ProductStatus
from product.models import Product

from .models import Brand


async def get_brands_with_counts_from_db(db: AsyncSession) -> list[tuple[Brand, int]]:
    """
    Retrieve all brands with their number of active products.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.

    Returns:
        list[tuple[Brand, int]]: Each brand with its active product count.
    """
    query = (
        select(Brand, func.count(Product.id))
        .outerjoin(
            Product,
            and_(
                Product.brand_id == Brand.id,
                Product.status == ProductStatus.ACTIVE.value,  # R1
            ),
        )
        .group_by(Brand.id)
        .order_by(Brand.name, Brand.id)
    )
    result = await db.execute(query)
    return [(brand, count) for brand, count in result.all()]
