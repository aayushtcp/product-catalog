from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import SlugMixin, StringIdMixin

if TYPE_CHECKING:
    from product.models import Product


class Brand(StringIdMixin, SlugMixin, Base):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="brand")
