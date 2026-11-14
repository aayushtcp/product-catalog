"""Database access for reviews."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums import ProductStatus
from pagination import PaginatedResult, PaginationParams, paginate_items
from product.models import Product

from .models import Review


async def get_active_product_id_by_slug(db: AsyncSession, slug: str) -> str | None:
    """
    Find the ID of a visible product by its slug.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        slug (str): Product slug, matched exactly.

    Returns:
        str | None: Product ID, or None if missing, draft or archived.
    """
    return await db.scalar(
        select(Product.id).where(
            Product.slug == slug, Product.status == ProductStatus.ACTIVE.value
        )
    )


async def get_reviews_from_db(
    db: AsyncSession, product_id: str, params: PaginationParams
) -> PaginatedResult:
    """
    Retrieve a page of reviews for a product, newest first.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        product_id (str): Product ID.
        params (PaginationParams): Validated page and limit.

    Returns:
        PaginatedResult: Reviews for the page and the total review count.
    """
    query = (
        select(Review)
        .where(Review.product_id == product_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    return await paginate_items(db, query, params)
