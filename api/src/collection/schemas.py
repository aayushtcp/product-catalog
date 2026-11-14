"""Schemas for the collection endpoints."""

from product.schemas import ProductCard
from schemas import CamelModel, Page


class CollectionBase(CamelModel):
    """
    Basic collection data.

    Attributes:
        slug (str): URL-friendly collection identifier.
        name (str): Collection name.
        description (str): Collection description.
    """

    slug: str
    name: str
    description: str


class CollectionOut(CollectionBase):
    """
    Collection in the list view.

    Attributes:
        product_count (int): Number of active products in the collection.
    """

    product_count: int


class CollectionDetail(CollectionBase):
    """
    Collection with a page of its products.

    Attributes:
        products (Page[ProductCard]): Paginated active products.
    """

    products: Page[ProductCard]
