from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import CreatedAtMixin, StringIdMixin

if TYPE_CHECKING:
    from product.models import Product


class Review(StringIdMixin, CreatedAtMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating"),
        Index(
            "ix_reviews_product_created",
            "product_id",
            text("created_at DESC"),
        ),
        Index("ix_reviews_product_rating", "product_id", "rating"),
    )

    # Columns
    product_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_purchase: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relations
    product: Mapped[Product] = relationship(back_populates="reviews")
