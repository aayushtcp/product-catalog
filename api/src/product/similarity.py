"""Similarity scoring between products."""

from decimal import Decimal

from .models import Product

SIMILAR_LIMIT = 4
MAX_CANDIDATES = 200

WEIGHT_SAME_SUBCATEGORY = 5
WEIGHT_SAME_MAIN_CATEGORY = 3
WEIGHT_SAME_BRAND = 3
WEIGHT_SAME_MATERIAL = 2
WEIGHT_SHARED_TAG = 1
MAX_SHARED_TAG_SCORE = 3
WEIGHT_SIMILAR_PRICE = 2
PRICE_TOLERANCE = Decimal("0.25")


def main_category_id(product: Product) -> str:
    """Return the main category ID (the parent of the sub-category)."""
    return product.category.parent_id or product.category_id


def material_of(product: Product) -> str | None:
    """Return the lowercase material, or None when unknown."""
    value = (product.attributes or {}).get("material")
    return str(value).strip().lower() if value else None


def score_similarity(target: Product, candidate: Product) -> int:
    """
    Score how much a candidate has in common with the target product.

    Args:
        target (Product): The product being viewed.
        candidate (Product): Another product to compare.

    Returns:
        int: Similarity score, higher means more similar.
    """
    score = 0

    if candidate.category_id == target.category_id:
        score += WEIGHT_SAME_SUBCATEGORY
    if main_category_id(candidate) == main_category_id(target):
        score += WEIGHT_SAME_MAIN_CATEGORY
    if candidate.brand_id == target.brand_id:
        score += WEIGHT_SAME_BRAND

    material = material_of(target)
    if material and material == material_of(candidate):
        score += WEIGHT_SAME_MATERIAL

    target_tags = {t.lower() for t in target.tags or []}
    candidate_tags = {t.lower() for t in candidate.tags or []}
    score += min(
        len(target_tags & candidate_tags) * WEIGHT_SHARED_TAG, MAX_SHARED_TAG_SCORE
    )

    if target.min_price and candidate.min_price is not None:
        gap = abs(candidate.min_price - target.min_price) / target.min_price
        if gap <= PRICE_TOLERANCE:
            score += WEIGHT_SIMILAR_PRICE

    return score


def pick_top_similar(
    target: Product, candidates: list[Product], limit: int = SIMILAR_LIMIT
) -> list[Product]:
    """
    Pick the most similar products: no self, no duplicates, sold-out last.

    Args:
        target (Product): The product being viewed.
        candidates (list[Product]): Visible products to rank.
        limit (int): Maximum number of products to return.

    Returns:
        list[Product]: Top products, in-stock first, then by score, then by ID.
    """
    unique = {c.id: c for c in candidates if c.id != target.id}
    ranked = sorted(
        unique.values(),
        key=lambda c: (not c.in_stock, -score_similarity(target, c), c.id),
    )
    return ranked[:limit]
