"""HTTP routes for reviews."""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from errors import handle_exception
from pagination import Pagination, PaginationParams
from schemas import ErrorResponse, Page

from .schemas import RatingSummary, ReviewOut
from .services import get_product_rating_summary, list_product_reviews

router = APIRouter(prefix="/api/products", tags=["reviews"])


@router.get(
    "/{slug}/reviews/",
    response_model=Page[ReviewOut],
    responses={404: {"model": ErrorResponse}},
    summary="List product reviews",
)
async def get_product_reviews(
    slug: str = Path(..., max_length=200),
    params: PaginationParams = Pagination,
    db: AsyncSession = Depends(get_db),
):
    """
    List reviews of a visible product, newest first.

    Args:
        slug (str): Product slug.
        params (PaginationParams): Validated page and limit.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Page of reviews with `items`, `page`, `limit`, `total`, `totalPages`.
    """
    try:
        return await list_product_reviews(db, slug, params)
    except Exception as error:
        return handle_exception(error)


@router.get(
    "/{slug}/reviews/summary/",
    response_model=RatingSummary,
    responses={404: {"model": ErrorResponse}},
    summary="Get the rating breakdown of a product",
)
async def get_product_rating_breakdown(
    slug: str = Path(..., max_length=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the rating breakdown of a visible product.

    Args:
        slug (str): Product slug.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Average rating, review count and one bucket per star rating.
    """
    try:
        return await get_product_rating_summary(db, slug)
    except Exception as error:
        return handle_exception(error)
