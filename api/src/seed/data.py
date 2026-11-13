"""Rows passed from catalog cleaning to the database loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Row = dict[str, Any]


@dataclass
class SeedData:
    brands: list[Row] = field(default_factory=list)
    categories: list[Row] = field(default_factory=list)
    products: list[Row] = field(default_factory=list)
    variants: list[Row] = field(default_factory=list)
    images: list[Row] = field(default_factory=list)
    reviews: list[Row] = field(default_factory=list)
    collections: list[Row] = field(default_factory=list)
    collection_products: list[Row] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
