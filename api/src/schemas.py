"""Shared schemas: SQLAlchemy model mixins and common Pydantic response models."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .constants import CONFIG_DICT_EXTRA_FORBID


# SQLAlchemy mixins
class StringIdMixin:
    """Primary key `id` as a string, e.g. `p001`, `b06`."""

    id: Mapped[str] = mapped_column(String, primary_key=True)


class SlugMixin:
    """Unique, indexed `slug` used as the public lookup key."""

    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)


class CreatedAtMixin:
    """`created_at` timestamp (UTC), set by the database on insert."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TimeStampMixin(CreatedAtMixin):
    """`created_at` plus `updated_at`, refreshed on every update."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Pydantic base + shared response models
T = TypeVar("T")


class CamelModel(BaseModel):
    """Base model: snake_case in Python, camelCase in JSON, ORM-friendly."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra=CONFIG_DICT_EXTRA_FORBID,
    )


class ErrorDetail(CamelModel):
    """One entry in an error's `details` list."""

    field: str | None = None
    value: Any = None
    message: str | None = None


class ErrorBody(CamelModel):
    """Inner error object: machine code, human message, optional details."""

    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(CamelModel):
    """The single error shape returned by every endpoint."""

    error: ErrorBody


class Page(CamelModel, Generic[T]):
    """Generic paginated response."""

    items: list[T]
    page: int
    limit: int
    total: int
    total_pages: int


class ImageOut(CamelModel):
    """Image with an absolute, browser-loadable URL."""

    url: str
    alt: str


class BrandRef(CamelModel):
    """Short brand reference used inside product responses."""

    slug: str
    name: str


class CategoryRef(CamelModel):
    """Short category reference used inside product responses."""

    slug: str
    name: str
