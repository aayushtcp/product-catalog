"""Business logic for the review endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from datatypes import JSONType
from errors import NotFoundError
from pagination import PaginationParams, build_page

from .repository import (
    get_active_product_id_by_slug,
    get_rating_counts,
    get_reviews_from_db,
)
from .schemas import RatingBucket, RatingSummary, ReviewOut

RATINGS = (5, 4, 3, 2, 1)


def build_rating_summary(counts: dict[int, int]) -> RatingSummary:
    """
    Build the rating breakdown from a mapping of rating to review count.

    Every rating from 5 down to 1 is always present, even when it has no
    reviews, so the UI can always render five rows.

    Args:
        counts (dict[int, int]): Number of reviews per star rating.

    Returns:
        RatingSummary: Average rating (None without reviews), total count and
        the five rating buckets.
    """
    total = sum(counts.values())
    average = (
        round(sum(rating * count for rating, count in counts.items()) / total, 1)
        if total
        else None
    )
    breakdown = [
        RatingBucket(rating=rating, count=counts.get(rating, 0)) for rating in RATINGS
    ]
    return RatingSummary(
        average=average,
        count=total,
        breakdown=breakdown,
    )


async def list_product_reviews(
    db: AsyncSession, slug: str, params: PaginationParams
) -> JSONType:
    """
    Retrieve a page of reviews for a visible product.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        slug (str): Product slug.
        params (PaginationParams): Validated page and limit.

    Returns:
        JSONType: Serialized page with `items`, `page`, `limit`, `total`
        and `totalPages`.

    Raises:
        NotFoundError: If the product does not exist or is not active.
    """
    product_id = await get_active_product_id_by_slug(db, slug)
    if product_id is None:
        raise NotFoundError(f"Product not found: {slug}")

    result = await get_reviews_from_db(db, product_id, params)
    items = [ReviewOut.model_validate(row) for row in result.items]
    return build_page(items, params, result.total).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True
    )


async def get_product_rating_summary(db: AsyncSession, slug: str) -> JSONType:
    """
    Retrieve the rating breakdown of a visible product.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        slug (str): Product slug.

    Returns:
        JSONType: Serialized summary with `average`, `count` and `breakdown`.

    Raises:
        NotFoundError: If the product does not exist or is not active.
    """
    product_id = await get_active_product_id_by_slug(db, slug)
    if product_id is None:
        raise NotFoundError(f"Product not found: {slug}")

    counts = await get_rating_counts(db, product_id)
    return build_rating_summary(counts).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True
    )
