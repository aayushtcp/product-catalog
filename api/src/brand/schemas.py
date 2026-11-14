"""Schemas for the brand endpoints."""

from schemas import CamelModel


class BrandOut(CamelModel):
    """
    Brand with its visible product count.

    Attributes:
        slug (str): URL-friendly brand identifier.
        name (str): Brand name.
        country (str | None): Country of the brand.
        product_count (int): Number of active products.
    """

    slug: str
    name: str
    country: str | None
    product_count: int
