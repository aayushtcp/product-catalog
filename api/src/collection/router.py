"""HTTP routes for collections."""

from fastapi import APIRouter, Depends, Path
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from errors import handle_exception
from pagination import Pagination, PaginationParams
from schemas import ErrorResponse

from .schemas import CollectionDetail, CollectionOut
from .services import get_collection_detail, list_collections

router = APIRouter(prefix="/api/collections", tags=["collections"])


@router.get("/", response_model=list[CollectionOut], summary="List visible collections")
async def get_collections(db: AsyncSession = Depends(get_db)):
    """
    List visible collections (R4) with their active product counts.

    Args:
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Collections sorted by name, each with `productCount`.
    """
    try:
        return await list_collections(db)
    except Exception as error:
        return handle_exception(error)


@router.get(
    "/{slug}/",
    response_model=CollectionDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Get collection with products",
)
async def get_collection(
    slug: Annotated[str, Path(max_length=200)],
    params: PaginationParams = Pagination,
    db: AsyncSession = Depends(get_db),
):
    """
    Get one visible collection with a page of its active products.

    Args:
        slug (str): Collection slug.
        params (PaginationParams): Validated page and limit.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Collection with `products` (`items`, `page`, `limit`, `total`, `totalPages`).
    """
    try:
        return await get_collection_detail(db, slug, params)
    except Exception as error:
        return handle_exception(error)
