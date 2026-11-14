"""Pagination params dependency, page helpers and the paginated-query helper."""

import math
import os
from dataclasses import dataclass
from typing import Any, Sequence

from fastapi import Depends, Query
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from constants import (
    DEFAULT_PAGINATION_PAGE_NUMBER,
    DEFAULT_PAGINATION_PAGE_SIZE,
    PAGINATION_PAGE_NUMBER,
    PAGINATION_PAGE_SIZE,
)
from schemas import Page

MAX_LIMIT = 50


def _env_positive_int(key: str, default: int) -> int:
    """Read a positive int from the environment; fall back to `default`."""
    try:
        value = int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default
    return value if value >= 1 else default


DEFAULT_PAGE = _env_positive_int(PAGINATION_PAGE_NUMBER, DEFAULT_PAGINATION_PAGE_NUMBER)
DEFAULT_LIMIT = min(
    _env_positive_int(PAGINATION_PAGE_SIZE, DEFAULT_PAGINATION_PAGE_SIZE), MAX_LIMIT
)


@dataclass(frozen=True)
class PaginationParams:
    """
    Validated `page` and `limit` query parameters.

    Attributes:
        page (int): Page number, starting at 1.
        limit (int): Items per page.
    """

    page: int = DEFAULT_PAGE
    limit: int = DEFAULT_LIMIT

    @property
    def offset(self) -> int:
        """Number of rows to skip for this page."""
        return (self.page - 1) * self.limit


@dataclass(frozen=True)
class PaginatedResult:
    """
    Raw result of a paginated database query.

    Attributes:
        items (list[Any]): ORM entities for the requested page.
        total (int): Total number of rows matching the query.
    """

    items: list[Any]
    total: int


def pagination_params(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
) -> PaginationParams:
    """FastAPI dependency: invalid page or limit becomes a 400 error."""
    return PaginationParams(page=page, limit=limit)


Pagination = Depends(pagination_params)


def total_pages(total: int, limit: int) -> int:
    """Number of pages for `total` rows (0 when empty)."""
    return math.ceil(total / limit) if total else 0


def build_page(items: Sequence[Any], params: PaginationParams, total: int) -> Page:
    """Wrap serialized items and metadata in the shared `Page` response."""
    return Page(
        items=list(items),
        page=params.page,
        limit=params.limit,
        total=total,
        total_pages=total_pages(total, params.limit),
    )


async def paginate_items(
    db: AsyncSession, query: Select, params: PaginationParams
) -> PaginatedResult:
    """
    Run a single-entity query with LIMIT/OFFSET in the database.

    Args:
        db (AsyncSession): SQLAlchemy async DB session.
        query (Select): Query selecting one ORM entity, already ordered with a
            stable final sort key (for example `Product.id`).
        params (PaginationParams): Validated page and limit.

    Returns:
        PaginatedResult: Entities for the requested page and the total row count.
    """
    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset(params.offset).limit(params.limit))
    return PaginatedResult(items=list(result.scalars().unique().all()), total=total)
