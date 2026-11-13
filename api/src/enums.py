"""Shared enums used by models, query params and responses."""

from enum import Enum


class ProductStatus(str, Enum):
    """Product lifecycle state. Only `active` is visible (R1)."""

    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"


class ProductSort(str, Enum):
    """Allowed values for `GET /api/products?sort=`."""

    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"
    RATING = "rating"
    POPULAR = "popular"
