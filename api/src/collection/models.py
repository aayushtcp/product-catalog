from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import SlugMixin, StringIdMixin

if TYPE_CHECKING:
    from product.models import Product


collection_products = Table(
    "collection_products",
    Base.metadata,
    Column(
        "collection_id",
        String(10),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "product_id",
        String(10),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

Index(
    "ix_collection_products_product_id",
    collection_products.c.product_id,
)


class Collection(StringIdMixin, SlugMixin, Base):
    __tablename__ = "collections"
    __table_args__ = (
        Index(
            "ix_collections_active_dates",
            "is_active",
            "starts_at",
            "ends_at",
            postgresql_where=text("is_active IS TRUE"),
        ),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    products: Mapped[list[Product]] = relationship(
        secondary=collection_products,
        back_populates="collections",
    )
