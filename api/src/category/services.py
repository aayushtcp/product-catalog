"""Business logic for the category endpoints."""

from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from datatypes import JSONType

from .repository import get_categories_with_counts_from_db
from .schemas import CategoryNode


async def get_category_tree(db: AsyncSession) -> list[JSONType]:
    """
    Retrieve the category tree with active product counts.

    Args:
        db (AsyncSession): Async SQLAlchemy session.

    Returns:
        list[JSONType]: Main categories with their sub-categories. A main
        category's count includes its sub-categories.
    """
    rows = await get_categories_with_counts_from_db(db)

    children: dict[str, list[CategoryNode]] = defaultdict(list)
    for category, count in rows:
        if category.parent_id:
            children[category.parent_id].append(
                CategoryNode(
                    slug=category.slug, name=category.name, product_count=count
                )
            )

    tree = [
        CategoryNode(
            slug=category.slug,
            name=category.name,
            product_count=count + sum(c.product_count for c in children[category.id]),
            children=children[category.id],
        )
        for category, count in rows
        if category.parent_id is None
    ]
    return [
        node.model_dump(mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True)
        for node in tree
    ]
