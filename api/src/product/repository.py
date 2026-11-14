"""Database access for products."""

from typing import Any

from sqlalchemy import ColumnElement, Select, Text, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from brand.models import Brand
from category.models import Category
from enums import ProductSort, ProductStatus
from pagination import PaginatedResult, PaginationParams, paginate_items
from .models import Product
from .schemas import ProductFilters
from .similarity import MAX_CANDIDATES, material_of, main_category_id

Parent = aliased(Category)


def _like(term: str) -> str:
    """Escape LIKE wildcards in `term` and wrap it as a contains pattern."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _search_condition(term: str) -> ColumnElement[bool]:
    """Match one search term against every searchable field (case-insensitive)."""
    pattern = _like(term)
    fields = (
        Product.name,
        Product.description,
        Brand.name,
        Category.name,
        Parent.name,
        Product.attributes["material"].as_string(),
        cast(Product.tags, Text),
    )
    return or_(*(field.ilike(pattern, escape="\\") for field in fields))


def _order_by(sort: ProductSort) -> list[Any]:
    """Return ORDER BY clauses; `Product.id` is always last for stable paging."""
    primary = {
        ProductSort.PRICE_ASC: Product.min_price.asc().nulls_last(),
        ProductSort.PRICE_DESC: Product.min_price.desc().nulls_last(),
        ProductSort.NEWEST: Product.created_at.desc(),
        ProductSort.RATING: Product.rating_average.desc().nulls_last(),
        ProductSort.POPULAR: Product.sales_count.desc(),
    }[sort]
    return [primary, Product.id.asc()]


def _build_products_query(filters: ProductFilters) -> Select:
    """Build the filtered and sorted product query."""
    query = (
        select(Product)
        .join(Brand, Product.brand_id == Brand.id)
        .join(Category, Product.category_id == Category.id)
        .outerjoin(Parent, Category.parent_id == Parent.id)
        .options(
            contains_eager(Product.brand),
            contains_eager(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
        )
        # R1: only active products are visible.
        .where(Product.status == ProductStatus.ACTIVE.value)
    )

    # R2: price filters use the lowest variant price (Product.min_price).
    if filters.min_price is not None:
        query = query.where(Product.min_price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Product.min_price <= filters.max_price)
    # R3: in stock means at least one variant has stock.
    if filters.in_stock:
        query = query.where(Product.in_stock.is_(True))
    if filters.min_rating is not None:
        query = query.where(Product.rating_average >= filters.min_rating)
    if filters.brand_slugs:
        query = query.where(Brand.slug.in_(filters.brand_slugs))
    if filters.category_slug:
        slug = filters.category_slug
        query = query.where(or_(Category.slug == slug, Parent.slug == slug))
    for term in filters.search_terms:
        query = query.where(_search_condition(term))

    return query.order_by(*_order_by(filters.sort))


async def get_category_id_by_slug(db: AsyncSession, slug: str) -> str | None:
    """
    Find a category ID by its slug.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        slug (str): Category slug.

    Returns:
        str | None: Category ID, or None if the slug does not exist.
    """
    return await db.scalar(select(Category.id).where(Category.slug == slug))


async def get_existing_brand_slugs(db: AsyncSession, slugs: list[str]) -> set[str]:
    """
    Return which of the given brand slugs exist.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        slugs (list[str]): Brand slugs to check.

    Returns:
        set[str]: Slugs that exist in the database.
    """
    result = await db.scalars(select(Brand.slug).where(Brand.slug.in_(slugs)))
    return set(result.all())


async def get_products_from_db(
    db: AsyncSession, filters: ProductFilters, params: PaginationParams
) -> PaginatedResult:
    """
    Retrieve a page of visible products matching the filters.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        filters (ProductFilters): Search, filter and sort options.
        params (PaginationParams): Validated page and limit.

    Returns:
        PaginatedResult: Products for the page and the total match count.
    """
    return await paginate_items(db, _build_products_query(filters), params)


# Product detail
async def get_product_by_slug_from_db(db: AsyncSession, slug: str) -> Product | None:
    """
    Retrieve one visible product with its brand, images and variants.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        slug (str): Product slug, matched exactly.

    Returns:
        Product | None: The active product, or None if missing, draft or archived.
    """
    query = (
        select(Product)
        .where(Product.slug == slug, Product.status == ProductStatus.ACTIVE.value)
        .options(
            joinedload(Product.brand),
            joinedload(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
        )
    )
    return await db.scalar(query)


async def get_category_path_from_db(
    db: AsyncSession, category_id: str
) -> list[Category]:
    """
    Retrieve a category with its parent.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        category_id (str): ID of the product's sub-category.

    Returns:
        list[Category]: Main category first, then the sub-category (empty if not found).
    """
    result = await db.execute(
        select(Category, Parent)
        .outerjoin(Parent, Category.parent_id == Parent.id)
        .where(Category.id == category_id)
    )
    row = result.first()
    if row is None:
        return []
    category, parent = row
    return [parent, category] if parent else [category]


# Similar Product Using similarity simple algorithm
async def get_similar_candidates_from_db(
    db: AsyncSession, product: Product
) -> list[Product]:
    """
    Retrieve visible products that share something with the given product.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        product (Product): The product being viewed (brand and category loaded).

    Returns:
        list[Product]: Active products, never the product itself, that share the
        sub-category, main category, brand or material.
    """
    signals = [
        Product.category_id == product.category_id,
        Category.parent_id == main_category_id(product),
        Product.brand_id == product.brand_id,
    ]
    material = material_of(product)
    if material:
        signals.append(
            func.lower(Product.attributes["material"].as_string()) == material
        )

    query = (
        select(Product)
        .join(Brand, Product.brand_id == Brand.id)
        .join(Category, Product.category_id == Category.id)
        .options(
            contains_eager(Product.brand),
            contains_eager(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
        )
        .where(
            Product.status == ProductStatus.ACTIVE.value,  # R1
            Product.id != product.id,
            or_(*signals),
        )
        .order_by(Product.id)
        .limit(MAX_CANDIDATES)
    )
    result = await db.scalars(query)
    return list(result.unique().all())
