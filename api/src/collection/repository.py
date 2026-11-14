"""Database access for collections."""

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from brand.models import Brand
from category.models import Category
from enums import ProductStatus
from pagination import PaginatedResult, PaginationParams, paginate_items
from product.models import Product

from .models import Collection, collection_products

# R4: active, and now is between startsAt and endsAt (NULL means no limit).
VISIBLE = (
    Collection.is_active.is_(True),
    or_(Collection.starts_at.is_(None), Collection.starts_at <= func.now()),
    or_(Collection.ends_at.is_(None), Collection.ends_at >= func.now()),
)


async def get_visible_collections_from_db(
    db: AsyncSession,
) -> list[tuple[Collection, int]]:
    """
    Retrieve visible collections with their number of active products.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.

    Returns:
        list[tuple[Collection, int]]: Each visible collection with its product count.
    """
    query = (
        select(Collection, func.count(Product.id))
        .outerjoin(
            collection_products,
            collection_products.c.collection_id == Collection.id,
        )
        .outerjoin(
            Product,
            and_(
                Product.id == collection_products.c.product_id,
                Product.status == ProductStatus.ACTIVE.value,  # R1
            ),
        )
        .where(*VISIBLE)
        .group_by(Collection.id)
        .order_by(Collection.name, Collection.id)
    )
    result = await db.execute(query)
    return [(collection, count) for collection, count in result.all()]


async def get_visible_collection_by_slug_from_db(
    db: AsyncSession, slug: str
) -> Collection | None:
    """
    Find a visible collection by its slug.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        slug (str): Collection slug, matched exactly.

    Returns:
        Collection | None: The collection, or None if missing, inactive or outside its dates.
    """
    return await db.scalar(select(Collection).where(Collection.slug == slug, *VISIBLE))


async def get_collection_products_from_db(
    db: AsyncSession, collection_id: str, params: PaginationParams
) -> PaginatedResult:
    """
    Retrieve a page of active products in a collection.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        collection_id (str): Collection ID.
        params (PaginationParams): Validated page and limit.

    Returns:
        PaginatedResult: Products for the page and the total product count.
    """
    query = (
        select(Product)
        .join(collection_products, collection_products.c.product_id == Product.id)
        .join(Brand, Product.brand_id == Brand.id)
        .join(Category, Product.category_id == Category.id)
        .options(
            contains_eager(Product.brand),
            contains_eager(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
        )
        .where(
            collection_products.c.collection_id == collection_id,
            Product.status == ProductStatus.ACTIVE.value,  # R1
        )
        .order_by(Product.name, Product.id)
    )
    return await paginate_items(db, query, params)
