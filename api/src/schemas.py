from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class StringIdMixin:
    """Primary key mixin for stable catalog or generated string IDs."""

    id: Mapped[str] = mapped_column(String(10), primary_key=True)


class SlugMixin:
    """Slug String Mixin"""
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
