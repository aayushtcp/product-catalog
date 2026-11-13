"""Write prepared seed rows to PostgreSQL."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Table, delete, func, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import (
    Brand,
    Category,
    Collection,
    Product,
    ProductImage,
    Review,
    Variant,
    collection_products,
)
from seed.data import Row, SeedData

COUNTED_MODELS = (
    Brand,
    Category,
    Product,
    Variant,
    ProductImage,
    Review,
    Collection,
)


async def load_seed_data(data: SeedData) -> None:
    """Upsert all rows in one transaction. Derived rows are replaced exactly."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for model, rows, conflict_columns in (
                (Brand, data.brands, ["id"]),
                (Category, data.categories, ["id"]),
                (Product, data.products, ["id"]),
                (Variant, data.variants, ["sku"]),
                (Review, data.reviews, ["id"]),
                (Collection, data.collections, ["id"]),
            ):
                await _upsert(session, model, rows, conflict_columns)

            await _replace(session, ProductImage.__table__, data.images)
            await _replace(session, collection_products, data.collection_products)


async def _upsert(
    session: AsyncSession,
    model: type[Any],
    rows: list[Row],
    conflict_columns: list[str],
) -> None:
    if not rows:
        return

    table = model.__table__
    statement = pg_insert(table).values(rows)
    updates = {
        column: getattr(statement.excluded, column)
        for column in rows[0]
        if column not in conflict_columns
    }
    if updates:
        statement = statement.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=updates,
        )
    else:
        statement = statement.on_conflict_do_nothing(
            index_elements=conflict_columns,
        )

    await session.execute(statement)


async def _replace(
    session: AsyncSession,
    table: Table,
    rows: list[Row],
) -> None:
    await session.execute(delete(table))
    if rows:
        await session.execute(insert(table).values(rows))


async def count_rows() -> dict[str, int]:
    counts: dict[str, int] = {}
    async with AsyncSessionLocal() as session:
        for model in COUNTED_MODELS:
            result = await session.execute(select(func.count()).select_from(model))
            counts[model.__tablename__] = result.scalar_one()

        result = await session.execute(
            select(func.count()).select_from(collection_products)
        )
        counts[collection_products.name] = result.scalar_one()

    return counts
