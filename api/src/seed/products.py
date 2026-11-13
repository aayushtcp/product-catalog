"""Build product, variant and image rows from raw products."""

from __future__ import annotations

from typing import Any

from seed.data import Row
from seed.parsing import (
    clean_attributes,
    ensure_reference,
    ensure_unique,
    parse_datetime,
    to_decimal,
)


def build_products(
    products: list[dict[str, Any]],
    brand_ids: set[str],
    category_ids: set[str],
    issues: list[str],
) -> tuple[list[Row], list[Row], list[Row]]:
    rows: list[Row] = []
    variants: list[Row] = []
    images: list[Row] = []
    products_without_images: list[str] = []
    invalid_sale_prices: list[str] = []
    hidden_products: list[str] = []
    dropped_attributes = 0

    for product in products:
        product_id = product["id"]
        ensure_reference(
            brand_ids, product["brandId"], "brand", f"Product {product_id}"
        )
        ensure_reference(
            category_ids,
            product["categoryId"],
            "category",
            f"Product {product_id}",
        )

        product_variants = _build_variants(product, invalid_sale_prices)
        variants.extend(product_variants)
        images.extend(_build_images(product, products_without_images))

        attributes, dropped = clean_attributes(product.get("attributes"))
        dropped_attributes += dropped
        if product["status"] != "active":
            hidden_products.append(product_id)

        rows.append(
            {
                "id": product_id,
                "slug": product["slug"],
                "name": product["name"],
                "description": product["description"],
                "brand_id": product["brandId"],
                "category_id": product["categoryId"],
                "status": product["status"],
                "tags": product.get("tags") or [],
                "features": product.get("features") or [],
                "attributes": attributes,
                "rating_average": to_decimal(product.get("ratingAverage")),
                "review_count": int(product.get("reviewCount") or 0),
                "views": int(product.get("views") or 0),
                "sales_count": int(product.get("salesCount") or 0),
                "min_price": min(variant["price"] for variant in product_variants),
                "in_stock": any(variant["stock"] > 0 for variant in product_variants),
                "created_at": parse_datetime(product["createdAt"]),
                "updated_at": parse_datetime(product["updatedAt"]),
            }
        )

    ensure_unique(rows, "id", "product id")
    ensure_unique(rows, "slug", "product slug")
    ensure_unique(variants, "sku", "variant sku")

    if dropped_attributes:
        issues.append(f"Dropped {dropped_attributes} null attribute value(s)")
    issues.extend(
        f"Product {product_id} has no images" for product_id in products_without_images
    )
    issues.extend(
        f"{issue}; stored as-is, R5 will ignore the invalid old price"
        for issue in invalid_sale_prices
    )
    if hidden_products:
        issues.append(
            f"Imported {len(hidden_products)} non-active product(s) "
            f"({', '.join(hidden_products)}); R1 hides them at query time"
        )

    return rows, variants, images


def _build_variants(
    product: dict[str, Any],
    invalid_sale_prices: list[str],
) -> list[Row]:
    rows: list[Row] = []
    for index, variant in enumerate(product["variants"]):
        options = variant.get("options") or {}
        price = to_decimal(variant["price"])
        compare_at_price = to_decimal(variant.get("compareAtPrice"))

        if (
            price is not None
            and compare_at_price is not None
            and compare_at_price <= price
        ):
            invalid_sale_prices.append(
                f"Product {product['id']} / {variant['sku']}: "
                f"compareAtPrice {compare_at_price} <= price {price}"
            )

        rows.append(
            {
                "id": f"{product['id']}-v{index}",
                "product_id": product["id"],
                "sku": variant["sku"],
                "color": options.get("color"),
                "size": options.get("size"),
                "price": price,
                "compare_at_price": compare_at_price,
                "stock": int(variant["stock"]),
            }
        )

    if not rows:
        raise ValueError(f"Product {product['id']} has no variants")
    return rows


def _build_images(
    product: dict[str, Any],
    products_without_images: list[str],
) -> list[Row]:
    product_images = product.get("images") or []
    if not product_images:
        products_without_images.append(product["id"])

    return [
        {
            "id": f"{product['id']}-i{position}",
            "product_id": product["id"],
            "url": image["url"],
            "alt": image.get("alt"),
            "position": position,
        }
        for position, image in enumerate(product_images)
    ]
