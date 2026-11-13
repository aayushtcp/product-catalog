from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import SlugMixin, StringIdMixin, TimeStampMixin

if TYPE_CHECKING:
    from brand.models import Brand
    from category.models import Category
    from collection.models import Collection
    from review.models import Review


class Product(StringIdMixin, SlugMixin, TimeStampMixin, Base):
    __tablename__ = "products"

    # Table args for search index and rules
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'draft', 'archived')",
            name="ck_products_status",
        ),
        Index(
            "ix_products_status_active",
            "status",
            postgresql_where=text("status = 'active'"),
        ),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_brand_id", "brand_id"),
        Index("ix_products_min_price", "min_price"),
        Index(
            "ix_products_in_stock",
            "in_stock",
            postgresql_where=text("in_stock IS TRUE"),
        ),
        Index("ix_products_created_at", text("created_at DESC")),
        Index(
            "ix_products_rating_average",
            text("rating_average DESC NULLS LAST"),
        ),
        Index("ix_products_sales_count", text("sales_count DESC")),
        Index("ix_products_tags", "tags", postgresql_using="gin"),
        Index(
            "ix_products_attributes",
            "attributes",
            postgresql_using="gin",
            postgresql_ops={"attributes": "jsonb_path_ops"},
        ),
    )

    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    brand_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("brands.id"),
        nullable=False,
    )
    category_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("categories.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    features: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list,
    )
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    rating_average: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sales_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    brand: Mapped[Brand] = relationship(back_populates="products")
    category: Mapped[Category] = relationship(back_populates="products")
    variants: Mapped[list[Variant]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.position",
    )
    reviews: Mapped[list[Review]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    collections: Mapped[list[Collection]] = relationship(
        secondary="collection_products",
        back_populates="products",
    )


class Variant(StringIdMixin, Base):
    __tablename__ = "variants"

    # Table args for search index and calc, rules
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_variants_stock"),
        CheckConstraint("price >= 0", name="ck_variants_price"),
        UniqueConstraint(
            "product_id",
            "color",
            "size",
            name="uq_variants_product_color_size",
        ),
    )

    product_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    compare_at_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relations
    product: Mapped[Product] = relationship(back_populates="variants")


class ProductImage(StringIdMixin, Base):
    __tablename__ = "product_images"

    # Table args containg unique rule
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "position",
            name="uq_product_images_product_position",
        ),
    )

    product_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt: Mapped[str | None] = mapped_column(String(500), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relations
    product: Mapped[Product] = relationship(back_populates="images")
