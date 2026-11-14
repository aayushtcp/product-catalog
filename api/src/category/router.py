"""HTTP routes for categories."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from errors import handle_exception

from .schemas import CategoryNode
from .services import get_category_tree

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryNode], summary="List category tree")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    List main categories with their sub-categories and active product counts.

    Args:
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        data: Category tree; a main category's count includes its sub-categories.
    """
    try:
        return await get_category_tree(db)
    except Exception as error:
        return handle_exception(error)
