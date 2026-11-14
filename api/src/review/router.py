"""HTTP routes for reviews."""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from errors import handle_exception
from pagination import Pagination, PaginationParams
from schemas import ErrorResponse, Page

from .schemas import ReviewOut
from .services import list_product_reviews

router = APIRouter(prefix="/products", tags=["reviews"])


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
