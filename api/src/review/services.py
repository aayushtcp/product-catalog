"""Business logic for the review endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from datatypes import JSONType
from errors import NotFoundError
from pagination import PaginationParams, build_page

from .repository import get_active_product_id_by_slug, get_reviews_from_db
from .schemas import ReviewOut


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
