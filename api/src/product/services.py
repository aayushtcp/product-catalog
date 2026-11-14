"""Business logic for the product endpoints."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from errors import ValidationApiError, NotFoundError
from pagination import PaginationParams, build_page
from schemas import BrandRef, CategoryRef
from datatypes import JSONType
from serializers import image_out, to_float

from .models import Product
from .repository import (
    get_category_id_by_slug,
    get_category_path_from_db,
    get_existing_brand_slugs,
    get_product_by_slug_from_db,
    get_products_from_db,
    get_similar_candidates_from_db,
)
from .schemas import ProductCard, ProductDetail, ProductFilters, VariantOut
from .similarity import pick_top_similar


def _sale_compare_at_price(
    price: Decimal | None, compare_at_price: Decimal | None
) -> Decimal | None:
    """R5: return the old price only when it is greater than the current price."""
    if price is None or compare_at_price is None:
        return None
    return compare_at_price if compare_at_price > price else None


def _to_card(product: Product) -> ProductCard:
    """Convert a loaded `Product` into a `ProductCard`."""
    variants = product.variants
    cheapest = min(variants, key=lambda v: (v.price, v.sku), default=None)
    highest = max((v.price for v in variants), default=None)
    compare_at = _sale_compare_at_price(
        product.min_price, cheapest.compare_at_price if cheapest else None
    )
    return ProductCard(
        id=product.id,
        slug=product.slug,
        name=product.name,
        brand=BrandRef(slug=product.brand.slug, name=product.brand.name),
        category=CategoryRef(slug=product.category.slug, name=product.category.name),
        price=to_float(product.min_price),
        price_max=to_float(highest),
        compare_at_price=to_float(compare_at),
        in_stock=bool(product.in_stock),
        rating_average=to_float(product.rating_average),
        review_count=product.review_count or 0,
        image=image_out(product.images[0] if product.images else None),
    )


async def _validate_slugs(db: AsyncSession, filters: ProductFilters) -> None:
    """
    Check that the category and brand slugs in the filters exist.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        filters (ProductFilters): Filters from the request.

    Raises:
        ValidationApiError: If the category or any brand slug is unknown.
    """
    if filters.category_slug:
        if await get_category_id_by_slug(db, filters.category_slug) is None:
            raise ValidationApiError(
                f"Unknown category: {filters.category_slug}",
                [{"field": "category", "value": filters.category_slug}],
            )

    if filters.brand_slugs:
        known = await get_existing_brand_slugs(db, filters.brand_slugs)
        unknown = [slug for slug in filters.brand_slugs if slug not in known]
        if unknown:
            raise ValidationApiError(
                f"Unknown brand: {', '.join(unknown)}",
                [{"field": "brand", "value": slug} for slug in unknown],
            )


def _to_variant(variant) -> VariantOut:
    """Convert a variant row into `VariantOut`, applying R5 to its old price."""
    return VariantOut(
        sku=variant.sku,
        color=variant.color,
        size=variant.size,
        price=float(variant.price),
        compare_at_price=to_float(
            _sale_compare_at_price(variant.price, variant.compare_at_price)
        ),
        stock=variant.stock,
    )


def _to_detail(product: Product, category_path: list) -> ProductDetail:
    """Convert a loaded `Product` into a `ProductDetail`."""
    variants = sorted(product.variants, key=lambda v: (v.price, v.sku))
    return ProductDetail(
        id=product.id,
        slug=product.slug,
        name=product.name,
        description=product.description,
        brand=BrandRef(slug=product.brand.slug, name=product.brand.name),
        category_path=[CategoryRef(slug=c.slug, name=c.name) for c in category_path],
        attributes={
            k: v for k, v in (product.attributes or {}).items() if v is not None
        },
        features=product.features or [],
        images=[image for i in product.images if (image := image_out(i))],
        variants=[_to_variant(v) for v in variants],
        rating_average=to_float(product.rating_average),
        review_count=product.review_count or 0,
    )


async def list_products(
    db: AsyncSession, filters: ProductFilters, params: PaginationParams
) -> JSONType:
    """
    Retrieve a page of visible products.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        filters (ProductFilters): Search, filter and sort options.
        params (PaginationParams): Validated page and limit.

    Returns:
        JSONType: Serialized page with `items`, `page`, `limit`, `total`
        and `totalPages`.
    """
    await _validate_slugs(db, filters)
    result = await get_products_from_db(db, filters, params)
    items = [_to_card(product) for product in result.items]
    return build_page(items, params, result.total).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True
    )


# Product Detail
async def get_product_detail(db: AsyncSession, slug: str) -> JSONType:
    """
    Retrieve one visible product by slug.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        slug (str): Product slug.

    Returns:
        JSONType: Serialized product with brand, category path, attributes,
        features, images and variants.

    Raises:
        NotFoundError: If the product does not exist or is not active.
    """
    product = await get_product_by_slug_from_db(db, slug)
    if product is None:
        raise NotFoundError(f"Product not found: {slug}")

    category_path = await get_category_path_from_db(db, product.category_id)
    return _to_detail(product, category_path).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True
    )


# Similar Product
async def get_similar_products(db: AsyncSession, slug: str) -> list[JSONType]:
    """
    Retrieve up to 4 products similar to the given one.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        slug (str): Product slug.

    Returns:
        list[JSONType]: Serialized product cards, best match first.

    Raises:
        NotFoundError: If the product does not exist or is not active.
    """
    product = await get_product_by_slug_from_db(db, slug)
    if product is None:
        raise NotFoundError(f"Product not found: {slug}")

    candidates = await get_similar_candidates_from_db(db, product)
    return [
        _to_card(p).model_dump(mode=SCHEMA_MODEL_DUMP_JSON_MODE, by_alias=True)
        for p in pick_top_similar(product, candidates)
    ]
