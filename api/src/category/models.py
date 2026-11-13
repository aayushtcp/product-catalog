from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import SlugMixin, StringIdMixin

if TYPE_CHECKING:
    from product.models import Product


class Category(StringIdMixin, SlugMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (Index("ix_categories_parent_id", "parent_id"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Category | None] = relationship(
        back_populates="children",
        remote_side="Category.id",
    )
    children: Mapped[list[Category]] = relationship(back_populates="parent")
    products: Mapped[list[Product]] = relationship(back_populates="category")
