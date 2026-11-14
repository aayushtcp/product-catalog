"""Schemas for the product endpoints."""

from pydantic import BaseModel
from typing import Any

from enums import ProductSort
from schemas import BrandRef, CamelModel, CategoryRef, ImageOut


class ProductCard(CamelModel):
    """
    Product summary used in product lists.

    Attributes:
        id (str): Product ID.
        slug (str): URL-friendly product identifier.
        name (str): Product name.
        brand (BrandRef): Brand of the product.
        category (CategoryRef): Sub-category of the product.
        price (float | None): Lowest variant price.
        price_max (float | None): Highest variant price, for "from €..." display.
        compare_at_price (float | None): Old price, only when on sale.
        in_stock (bool): True if at least one variant is in stock.
        rating_average (float | None): Average rating, None when unrated.
        review_count (int): Number of reviews.
        image (ImageOut | None): First product image, None when there is none.
    """

    id: str
    slug: str
    name: str
    brand: BrandRef
    category: CategoryRef
    price: float | None
    price_max: float | None
    compare_at_price: float | None
    in_stock: bool
    rating_average: float | None
    review_count: int
    image: ImageOut | None


class ProductFilters(BaseModel):
    """
    Filters for the product list, as received from the query string.

    Attributes:
        q (str | None): Raw search text.
        category (str | None): Category slug (a main category includes its children).
        brand (str | None): Comma-separated brand slugs.
        min_price (float | None): Inclusive minimum price.
        max_price (float | None): Inclusive maximum price.
        in_stock (bool | None): True keeps only in-stock products.
        min_rating (float | None): Minimum average rating (1-5).
        sort (ProductSort): Sort order.
    """

    q: str | None = None
    category: str | None = None
    brand: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    in_stock: bool | None = None
    min_rating: float | None = None
    sort: ProductSort = ProductSort.NEWEST

    @property
    def search_terms(self) -> list[str]:
        """Search words with extra spaces ignored."""
        return self.q.split() if self.q else []

    @property
    def category_slug(self) -> str | None:
        """Trimmed category slug, or None when empty."""
        return (self.category or "").strip() or None

    @property
    def brand_slugs(self) -> list[str]:
        """Unique, trimmed brand slugs in the order given."""
        parts = (self.brand or "").split(",")
        return list(dict.fromkeys(p.strip() for p in parts if p.strip()))


class VariantOut(CamelModel):
    """
    Purchasable variant of a product.

    Attributes:
        sku (str): Unique variant code.
        color (str | None): Variant color.
        size (str | None): Variant size.
        price (float): Variant price in EUR.
        compare_at_price (float | None): Old price, only when on sale.
        stock (int): Units in stock, 0 means sold out.
    """

    sku: str
    color: str | None
    size: str | None
    price: float
    compare_at_price: float | None
    stock: int


class ProductDetail(CamelModel):
    """
    Full product data for the detail page.

    Attributes:
        id (str): Product ID.
        slug (str): URL-friendly product identifier.
        name (str): Product name.
        description (str | None): Product description.
        brand (BrandRef): Brand of the product.
        category_path (list[CategoryRef]): Main category first, then sub-category.
        attributes (dict[str, Any]): Product details; empty values are left out.
        features (list[str]): Short selling points.
        images (list[ImageOut]): Product images, can be empty.
        variants (list[VariantOut]): Variants sorted by price.
        rating_average (float | None): Average rating, None when unrated.
        review_count (int): Number of reviews.
    """

    id: str
    slug: str
    name: str
    description: str | None
    brand: BrandRef
    category_path: list[CategoryRef]
    attributes: dict[str, Any]
    features: list[str]
    images: list[ImageOut]
    variants: list[VariantOut]
    rating_average: float | None
    review_count: int
