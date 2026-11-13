"""Import every model so SQLAlchemy registers all tables on Base.metadata."""

from brand.models import Brand
from category.models import Category
from collection.models import Collection, collection_products
from product.models import Product, ProductImage, Variant
from review.models import Review

__all__ = [
    "Brand",
    "Category",
    "Collection",
    "Product",
    "ProductImage",
    "Review",
    "Variant",
    "collection_products",
]
