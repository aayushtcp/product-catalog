"""Pagination params dependency, page metadata and a paginated-query helper."""

import math
import os
from dataclasses import dataclass
from typing import Any, Sequence

from fastapi import Depends, Query
from sqlalchemy import Row, Select, func, select
from sqlalchemy.orm import Session

from .constants import (
    DEFAULT_PAGINATION_PAGE_NUMBER,
    DEFAULT_PAGINATION_PAGE_SIZE,
    PAGINATION_PAGE_NUMBER,
    PAGINATION_PAGE_SIZE,
)
from .schemas import Page

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
    """Validated `page` / `limit` query params. Bad values become a 400."""

    page: int = DEFAULT_PAGE
    limit: int = DEFAULT_LIMIT

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


def pagination_params(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
) -> PaginationParams:
    """FastAPI dependency: `params: PaginationParams = Depends(pagination_params)`."""
    return PaginationParams(page=page, limit=limit)


Pagination = Depends(pagination_params)


def total_pages(total: int, limit: int) -> int:
    """Number of pages for `total` rows (0 when empty)."""
    return math.ceil(total / limit) if total else 0


def build_page(items: Sequence[Any], params: PaginationParams, total: int) -> Page:
    """Wrap already-serialized items in the shared `Page` response."""
    return Page(
        items=list(items),
        page=params.page,
        limit=params.limit,
        total=total,
        total_pages=total_pages(total, params.limit),
    )


def paginate(
    db: Session, stmt: Select, params: PaginationParams
) -> tuple[list[Row[Any]], int]:
    """Run `stmt` with LIMIT/OFFSET in the database; return (rows, total).

    `stmt` must already have a stable ORDER BY (end with `Product.id`).
    """
    total = (
        db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    )
    rows = list(db.execute(stmt.offset(params.offset).limit(params.limit)).all())
    return rows, total
