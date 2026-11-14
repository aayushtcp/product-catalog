"""Schemas for the category endpoints."""

from schemas import CamelModel


class CategoryNode(CamelModel):
    """
    Category with its visible product count and sub-categories.

    Attributes:
        slug (str): URL-friendly category identifier.
        name (str): Category name.
        product_count (int): Number of active products (main categories include their children).
        children (list[CategoryNode]): Sub-categories, empty for sub-categories.
    """

    slug: str
    name: str
    product_count: int
    children: list["CategoryNode"] = []
