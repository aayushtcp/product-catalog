"""Database access for categories."""

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from enums import ProductStatus
from product.models import Product

from .models import Category


async def get_categories_with_counts_from_db(
    db: AsyncSession,
) -> list[tuple[Category, int]]:
    """
    Retrieve all categories with their number of active products.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.

    Returns:
        list[tuple[Category, int]]: Each category with its own active product count.
    """
    query = (
        select(Category, func.count(Product.id))
        .outerjoin(
            Product,
            and_(
                Product.category_id == Category.id,
                Product.status == ProductStatus.ACTIVE.value,  # R1
            ),
        )
        .group_by(Category.id)
        .order_by(Category.name, Category.id)
    )
    result = await db.execute(query)
    return [(category, count) for category, count in result.all()]
