"""HTTP routes for brands."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from errors import handle_exception

from .schemas import BrandOut
from .services import get_all_brands

router = APIRouter(prefix="/api/brands", tags=["brands"])


@router.get("/", response_model=list[BrandOut], summary="List brands")
async def get_brands(db: AsyncSession = Depends(get_db)):
    """
    List all brands with their active product counts.

    Args:
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Brands sorted by name, each with `productCount`.
    """
    try:
        return await get_all_brands(db)
    except Exception as error:
        return handle_exception(error)
