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


class RatingBucket(CamelModel):
    """
    How many reviews have one star rating.

    Attributes:
        rating (int): The star rating, from 1 to 5.
        count (int): Number of reviews with this rating.
    """

    rating: int
    count: int


class RatingSummary(CamelModel):
    """
    Rating breakdown of a product's reviews.

    Attributes:
        average (float | None): Average rating, None when there are no reviews.
        count (int): Total number of reviews.
        breakdown (list[RatingBucket]): One bucket per star rating, 5 down to 1.
    """

    average: float | None
    count: int
    breakdown: list[RatingBucket]
