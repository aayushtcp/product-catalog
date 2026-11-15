"""Tests for the rating breakdown."""

from review.services import build_rating_summary


def test_rating_summary_without_reviews_has_no_average() -> None:
    summary = build_rating_summary({})

    assert summary.average is None
    assert summary.count == 0
    assert [bucket.rating for bucket in summary.breakdown] == [5, 4, 3, 2, 1]
    assert all(bucket.count == 0 for bucket in summary.breakdown)


def test_rating_summary_counts_match_the_reviews() -> None:
    summary = build_rating_summary({5: 9, 4: 4, 3: 3, 2: 1, 1: 1})

    assert summary.count == 18
    assert summary.average == 4.1
    assert [(bucket.rating, bucket.count) for bucket in summary.breakdown] == [
        (5, 9),
        (4, 4),
        (3, 3),
        (2, 1),
        (1, 1),
    ]


def test_rating_summary_keeps_missing_ratings_as_zero() -> None:
    summary = build_rating_summary({1: 3})

    assert summary.count == 3
    assert summary.average == 1.0
    assert [(bucket.rating, bucket.count) for bucket in summary.breakdown] == [
        (5, 0),
        (4, 0),
        (3, 0),
        (2, 0),
        (1, 3),
    ]
