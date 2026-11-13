"""Shared ORM-to-response helpers: absolute image URLs and Decimal to float."""

import os
from decimal import Decimal
from typing import Any

from .constants import API_BASE_URL_KEY
from .schemas import ImageOut


def base_url() -> str:
    """Public API base URL from `.env`, e.g. `http://localhost:2403`."""
    return os.getenv(API_BASE_URL_KEY, "http://localhost:2403").rstrip("/")


def image_url(path: str) -> str:
    """Turn a relative `images/p001-1.jpg` path into an absolute URL."""
    return f"{base_url()}/{path.lstrip('/')}"


def image_out(image: Any | None) -> ImageOut | None:
    """Convert an image row (`url`, `alt`) to `ImageOut`; `None` if missing."""
    if image is None:
        return None
    return ImageOut(url=image_url(image.url), alt=image.alt)


def to_float(value: Decimal | float | int | None) -> float | None:
    """Convert a Decimal price to float for JSON; keep `None`."""
    return None if value is None else float(value)
