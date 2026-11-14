"""Business logic for the collection endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from datatypes import JSONType
from errors import NotFoundError
from pagination import PaginationParams, build_page
from product.services import _to_card

from .repository import (
    get_collection_products_from_db,
    get_visible_collection_by_slug_from_db,
    get_visible_collections_from_db,
)
from .schemas import CollectionBase, CollectionOut


async def list_collections(db: AsyncSession) -> list[JSONType]:
    """
    Retrieve visible collections with their active product counts.

    Args:
        db (AsyncSession): Async SQLAlchemy session.

    Returns:
        list[JSONType]: Serialized collections, sorted by name.
    """
    rows = await get_visible_collections_from_db(db)
    return [
        CollectionOut(
            slug=c.slug, name=c.name, description=c.description, product_count=count
        ).model_dump(mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True)
        for c, count in rows
    ]


async def get_collection_detail(
    db: AsyncSession, slug: str, params: PaginationParams
) -> JSONType:
    """
    Retrieve one visible collection with a page of its products.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        slug (str): Collection slug.
        params (PaginationParams): Validated page and limit.

    Returns:
        JSONType: Collection data plus `products` with `items`, `page`,
        `limit`, `total` and `totalPages`.

    Raises:
        NotFoundError: If the collection does not exist or is not visible.
    """
    collection = await get_visible_collection_by_slug_from_db(db, slug)
    if collection is None:
        raise NotFoundError(f"Collection not found: {slug}")

    result = await get_collection_products_from_db(db, collection.id, params)
    items = [_to_card(product) for product in result.items]
    info = CollectionBase(
        slug=collection.slug, name=collection.name, description=collection.description
    ).model_dump(mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True)
    products = build_page(items, params, result.total).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True
    )
    return {**info, "products": products}
