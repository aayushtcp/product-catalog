"""Business logic for the brand endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from datatypes import JSONType

from .repository import get_brands_with_counts_from_db
from .schemas import BrandOut


async def get_all_brands(db: AsyncSession) -> list[JSONType]:
    """
    Retrieve all brands with their active product counts.

    Args:
        db (AsyncSession): Async SQLAlchemy session.

    Returns:
        list[JSONType]: Serialized brands, sorted by name.
    """
    rows = await get_brands_with_counts_from_db(db)
    return [
        BrandOut(
            slug=brand.slug, name=brand.name, country=brand.country, product_count=count
        ).model_dump(mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True)
        for brand, count in rows
    ]
