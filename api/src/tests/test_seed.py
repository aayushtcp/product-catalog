from __future__ import annotations

import copy
from datetime import timedelta
from decimal import Decimal
from typing import Any

import pytest

from seed.cleaning import prepare_seed_data
from seed.parsing import clean_attributes, parse_datetime


def make_catalog() -> dict[str, Any]:
    return {
        "brands": [
            {"id": "b01", "slug": "oakline", "name": "Oakline", "country": "DK"}
        ],
        "categories": [
            {"id": "c01", "slug": "home", "name": "Home", "parentId": None},
            {
                "id": "c02",
                "slug": "rugs",
                "name": "Rugs",
                "parentId": "c01",
            },
        ],
        "collections": [
            {
                "id": "col01",
                "slug": "sale",
                "name": "Sale",
                "description": "Sale items",
                "isActive": True,
                "startsAt": None,
                "endsAt": None,
                "productIds": ["p001", "p001"],
            }
        ],
        "products": [
            {
                "id": "p001",
                "slug": "shaggy-rug",
                "name": "Shaggy Rug",
                "description": "A rug",
                "brandId": "b01",
                "categoryId": "c02",
                "status": "active",
                "tags": ["wool"],
                "features": ["Handwoven"],
                "attributes": {"material": "Wool", "care": None},
                "images": [{"url": "images/p001-1.jpg", "alt": "Rug"}],
                "variants": [
                    {
                        "sku": "P001-CREAM-1",
                        "options": {"color": "Cream", "size": "120 x 170 cm"},
                        "price": 10.0,
                        "compareAtPrice": 20.0,
                        "stock": 0,
                    },
                    {
                        "sku": "P001-CREAM-2",
                        "options": {"color": "Cream", "size": "160 x 230 cm"},
                        "price": 5.0,
                        "compareAtPrice": None,
                        "stock": 3,
                    },
                ],
                "ratingAverage": 4.0,
                "reviewCount": 1,
                "views": 12,
                "salesCount": 2,
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-02T00:00:00Z",
            }
        ],
        "reviews": [
            {
                "id": "r001",
                "productId": "p001",
                "rating": 4,
                "title": "Nice",
                "body": None,
                "verifiedPurchase": True,
                "helpfulCount": 2,
                "createdAt": "2025-01-03T00:00:00Z",
            }
        ],
    }


def test_clean_attributes_drops_null_values() -> None:
    cleaned, dropped = clean_attributes(
        {"material": "Wool", "care": None, "origin": "Morocco"}
    )

    assert cleaned == {"material": "Wool", "origin": "Morocco"}
    assert dropped == 1


def test_parse_datetime_is_timezone_aware() -> None:
    parsed = parse_datetime("2025-01-01T00:00:00Z")

    assert parsed is not None
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == timedelta(0)


def test_prepare_seed_data_computes_prices_and_deduplicates_collections() -> None:
    data = prepare_seed_data(make_catalog())

    assert data.products[0]["min_price"] == Decimal("5.00")
    assert data.products[0]["in_stock"] is True
    assert data.products[0]["attributes"] == {"material": "Wool"}
    assert len(data.collection_products) == 1
    assert any("duplicate product ids" in issue for issue in data.issues)


def test_prepare_seed_data_rejects_duplicate_product_ids() -> None:
    catalog = make_catalog()
    catalog["products"].append(copy.deepcopy(catalog["products"][0]))
    catalog["products"][1]["slug"] = "other-rug"

    with pytest.raises(ValueError, match="Duplicate product id"):
        prepare_seed_data(catalog)
