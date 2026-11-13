"""Turn catalog.json into validated, database-ready rows."""

from __future__ import annotations

from typing import Any

from seed.data import Row, SeedData
from seed.parsing import (
    ensure_reference,
    ensure_unique,
    parse_datetime,
)
from seed.products import build_products


def prepare_seed_data(catalog: dict[str, Any]) -> SeedData:
    data = SeedData()
    data.brands = _build_brands(catalog["brands"])
    data.categories = _build_categories(catalog["categories"])

    brand_ids = {brand["id"] for brand in data.brands}
    category_ids = {category["id"] for category in data.categories}

    data.products, data.variants, data.images = build_products(
        catalog["products"],
        brand_ids,
        category_ids,
        data.issues,
    )

    product_ids = {product["id"] for product in data.products}
    data.reviews = _build_reviews(catalog["reviews"], product_ids)
    data.collections, data.collection_products = _build_collections(
        catalog["collections"],
        product_ids,
        data.issues,
    )

    return data


def _build_brands(brands: list[dict[str, Any]]) -> list[Row]:
    rows = [
        {
            "id": brand["id"],
            "slug": brand["slug"],
            "name": brand["name"],
            "country": brand["country"],
        }
        for brand in brands
    ]
    ensure_unique(rows, "id", "brand id")
    ensure_unique(rows, "slug", "brand slug")
    return rows


def _build_categories(categories: list[dict[str, Any]]) -> list[Row]:
    rows = [
        {
            "id": category["id"],
            "slug": category["slug"],
            "name": category["name"],
            "parent_id": category.get("parentId"),
        }
        for category in categories
    ]
    ensure_unique(rows, "id", "category id")
    ensure_unique(rows, "slug", "category slug")

    category_ids = {category["id"] for category in rows}
    for category in rows:
        parent_id = category["parent_id"]
        if parent_id is not None:
            ensure_reference(
                category_ids,
                parent_id,
                "category parent",
                f"Category {category['id']}",
            )

    rows.sort(key=lambda category: category["parent_id"] is not None)
    return rows


def _build_reviews(
    reviews: list[dict[str, Any]],
    product_ids: set[str],
) -> list[Row]:
    rows = []
    for review in reviews:
        ensure_reference(
            product_ids,
            review["productId"],
            "product",
            f"Review {review['id']}",
        )
        rows.append(
            {
                "id": review["id"],
                "product_id": review["productId"],
                "rating": int(review["rating"]),
                "title": review["title"],
                "body": review.get("body"),
                "verified_purchase": bool(review.get("verifiedPurchase", False)),
                "helpful_count": int(review.get("helpfulCount") or 0),
                "created_at": parse_datetime(review["createdAt"]),
            }
        )

    ensure_unique(rows, "id", "review id")
    return rows


def _build_collections(
    collections: list[dict[str, Any]],
    product_ids: set[str],
    issues: list[str],
) -> tuple[list[Row], list[Row]]:
    rows: list[Row] = []
    links: list[Row] = []
    seen_links: set[tuple[str, str]] = set()

    for collection in collections:
        product_ids_in_collection = collection.get("productIds") or []
        unique_product_ids = list(dict.fromkeys(product_ids_in_collection))
        if len(unique_product_ids) != len(product_ids_in_collection):
            issues.append(
                f"Collection {collection['id']} ({collection['slug']}) contains "
                "duplicate product ids; duplicates were removed"
            )

        for product_id in unique_product_ids:
            ensure_reference(
                product_ids,
                product_id,
                "product",
                f"Collection {collection['id']}",
            )
            pair = (collection["id"], product_id)
            if pair not in seen_links:
                seen_links.add(pair)
                links.append(
                    {
                        "collection_id": collection["id"],
                        "product_id": product_id,
                    }
                )

        rows.append(
            {
                "id": collection["id"],
                "slug": collection["slug"],
                "name": collection["name"],
                "description": collection.get("description") or "",
                "is_active": bool(collection.get("isActive", False)),
                "starts_at": parse_datetime(collection.get("startsAt")),
                "ends_at": parse_datetime(collection.get("endsAt")),
            }
        )

    ensure_unique(rows, "id", "collection id")
    ensure_unique(rows, "slug", "collection slug")
    return rows, links
