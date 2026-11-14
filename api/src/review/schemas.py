"""Schemas for the review endpoints."""

from datetime import datetime

from schemas import CamelModel


class ReviewOut(CamelModel):
    """
    Customer review of a product.

    Attributes:
        id (str): Review ID.
        rating (int): Rating from 1 to 5.
        title (str | None): Review title.
        body (str | None): Review text, None when the shopper left no text.
        verified_purchase (bool): True if the reviewer bought the product.
        helpful_count (int): How many shoppers marked the review as helpful.
        created_at (datetime): When the review was written.
    """

    id: str
    rating: int
    title: str | None
    body: str | None
    verified_purchase: bool
    helpful_count: int
    created_at: datetime
