"""Parse and validate raw catalog values."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from seed.data import Row


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def to_decimal(value: int | float | str | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def clean_attributes(attributes: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
    """Drop null values because missing and null mean the same thing."""
    source = attributes or {}
    cleaned = {key: value for key, value in source.items() if value is not None}
    return cleaned, len(source) - len(cleaned)


def ensure_unique(rows: list[Row], key: str, label: str) -> None:
    seen: set[Any] = set()
    for row in rows:
        value = row[key]
        if value in seen:
            raise ValueError(f"Duplicate {label} {key}: {value}")
        seen.add(value)


def ensure_reference(
    valid_ids: set[str],
    value: str,
    label: str,
    owner: str,
) -> None:
    if value not in valid_ids:
        raise ValueError(f"{owner} references unknown {label}: {value}")
