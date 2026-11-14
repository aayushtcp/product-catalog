"""HTTP routes for products."""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from enums import ProductSort
from errors import ValidationApiError, handle_exception
from pagination import Pagination, PaginationParams
from schemas import ErrorResponse, Page
from .schemas import ProductCard, ProductFilters, ProductDetail
from .services import list_products, get_product_detail, get_similar_products

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get(
    "/",
    response_model=Page[ProductCard],
    responses={400: {"model": ErrorResponse}},
    summary="List products",
)
async def get_products(
    q: str | None = Query(None, max_length=100),
    category: str | None = Query(None, max_length=100),
    brand: str | None = Query(None, max_length=300),
    min_price: float | None = Query(None, alias="minPrice", ge=0, allow_inf_nan=False),
    max_price: float | None = Query(None, alias="maxPrice", ge=0, allow_inf_nan=False),
    in_stock: bool | None = Query(None, alias="inStock"),
    min_rating: float | None = Query(
        None, alias="minRating", ge=1, le=5, allow_inf_nan=False
    ),
    sort: ProductSort = Query(ProductSort.NEWEST),
    params: PaginationParams = Pagination,
    db: AsyncSession = Depends(get_db),
):
    """
    List visible products with search, filters, sorting and pagination.

    Args:
        q (str | None): Search text; every word must match.
        category (str | None): Category slug; a main category includes its children.
        brand (str | None): Comma-separated brand slugs.
        min_price (float | None): Inclusive minimum price (`minPrice`).
        max_price (float | None): Inclusive maximum price (`maxPrice`).
        in_stock (bool | None): Only in-stock products when true (`inStock`).
        min_rating (float | None): Minimum rating from 1 to 5 (`minRating`).
        sort (ProductSort): Sort order. Defaults to `newest`.
        params (PaginationParams): Validated page and limit.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Page of products with `items`, `page`, `limit`, `total`, `totalPages`.
    """
    try:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationApiError(
                "minPrice must be less than or equal to maxPrice",
                [{"field": "minPrice", "value": min_price}],
            )
        filters = ProductFilters(
            q=q,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            min_rating=min_rating,
            sort=sort,
        )
        return await list_products(db, filters, params)
    except Exception as error:
        return handle_exception(error)


@router.get(
    "/{slug}/",
    response_model=ProductDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Get product detail",
)
async def get_product(
    slug: str = Path(..., max_length=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get one visible product by slug.

    Args:
        slug (str): Product slug.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Product with brand, category path, attributes, features, images and variants.
    """
    try:
        return await get_product_detail(db, slug)
    except Exception as error:
        return handle_exception(error)


# Similar Products
@router.get(
    "/{slug}/similar/",
    response_model=list[ProductCard],
    responses={404: {"model": ErrorResponse}},
    summary="Get similar products",
)
async def get_similar(
    slug: str = Path(..., max_length=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get up to 4 visible products similar to the given one.

    Args:
        slug (str): Product slug.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: List of up to 4 product cards, best match first.
    """
    try:
        return await get_similar_products(db, slug)
    except Exception as error:
        return handle_exception(error)
