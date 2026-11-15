# Product Catalog

A small home-and-living product catalog built from `data/catalog.json` and its
product images.

## Setup

Start everything with Docker:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

No `.env` file is required. Copy `.env.example` to `.env` only to change the
default ports or configuration. Docker starts PostgreSQL, the API seeds the
database, then the frontend starts. The seed is idempotent, so restarting does
not duplicate data.

To stop the app:

```bash
docker compose down
```

## Tech stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, and React Query.
- **API:** FastAPI and Pydantic.
- **Database:** PostgreSQL with SQLAlchemy and Alembic.
- **Docker:** Docker Compose runs the database, API, and frontend.

This stack keeps the frontend, API, and database separate while using familiar
tools for a small full-stack application.

## Database

```text
brands ──< products >── categories
              ├──< variants
              ├──< product_images
              ├──< reviews
              └──< collection_products >── collections
```

`categories.parent_id` links a sub-category to its main category.
`products.attributes` uses JSONB because attribute fields vary by product type.
`tags` and `features` use PostgreSQL text arrays.

The seed imports 120 products, 336 variants, 933 reviews, 160 images, and 8
collections. It upserts source rows and rebuilds image and collection links.

### Indexes

- `products.slug`, brand/category/collection slugs, and `variants.sku` are
  unique indexes for direct lookups.
- `products.status`, `category_id`, `brand_id`, `min_price`, `in_stock`,
  `created_at`, `rating_average`, and `sales_count` support product filters and
  sorting.
- GIN indexes on `products.tags` and `products.attributes` support tag and
  attribute searches.
- Review, image, variant, category-parent, and collection-link indexes support
  their related detail pages and lists.
- `reviews (product_id, rating)` supports the rating breakdown, which groups the
  reviews of one product by rating.

## API

All endpoints return JSON. Only active products are visible.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/products/` | Product list with filters, sorting, and pagination. |
| GET | `/api/products/{slug}/` | Product detail and variants. |
| GET | `/api/products/{slug}/reviews/` | Product reviews, newest first. |
| GET | `/api/products/{slug}/reviews/summary/` | Rating breakdown of a product's reviews. |
| GET | `/api/products/{slug}/similar/` | Up to four similar products. |
| GET | `/api/categories/` | Category tree with product counts. |
| GET | `/api/brands/` | Brands with product counts. |
| GET | `/api/collections/` | Currently visible collections. |
| GET | `/api/collections/{slug}/` | A collection and its products. |

`GET /api/products` supports:

| Parameter | Purpose |
| --- | --- |
| `q` | Search text. |
| `category` | Main or sub-category slug. |
| `brand` | Comma-separated brand slugs. |
| `minPrice`, `maxPrice` | Lowest variant price range. |
| `inStock` | `true` for products with stock. |
| `minRating` | Rating from 1 to 5. |
| `sort` | `price_asc`, `price_desc`, `newest`, `rating`, or `popular`. |
| `page`, `limit` | Pagination; default is page 1 and limit 12. |

Example:

```http
GET /api/products?q=candle&inStock=true&sort=price_asc&page=1&limit=2
```

```json
{
  "items": [{ "slug": "taper-candles-set-of-6", "name": "Taper Candles (Set of 6)", "price": 12.99, "inStock": true }],
  "page": 1,
  "limit": 2,
  "total": 7,
  "totalPages": 4
}
```

Errors use one shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Unknown category: unknown",
    "details": [{ "field": "category", "value": "unknown" }]
  }
}
```

Common codes are `VALIDATION_ERROR` (400), `NOT_FOUND` (404), and
`INTERNAL_ERROR` (500).

### Rating breakdown

`GET /api/products/{slug}/reviews/summary/` returns the star distribution of a
product's reviews:

```http
GET /api/products/shaggy-diamond-rug/reviews/summary/
```

```json
{
  "average": 4.1,
  "count": 18,
  "breakdown": [
    { "rating": 5, "count": 9 },
    { "rating": 4, "count": 4 },
    { "rating": 3, "count": 3 },
    { "rating": 2, "count": 1 },
    { "rating": 1, "count": 1 }
  ]
}
```

The counts come from a single `GROUP BY rating` query in PostgreSQL, so the
database does the aggregation and the API always receives five rows. It is a
separate endpoint from the review list so that paginating the reviews does not
recompute the breakdown. A product without reviews returns `average: null`,
`count: 0` and five empty buckets, and a hidden product returns `404`.

## Search

Search splits `q` into words. Every word must match at least one of: product
name, description, brand, category, material, or tags. Matching is
case-insensitive and partial (`handwov` matches `handwoven`).

It uses PostgreSQL `ILIKE`, so it has no typo tolerance or relevance ranking.
For a larger catalog, I would add PostgreSQL full-text search and `pg_trgm`.

## Similar products

Candidates must be active and share a category, brand, or material. They are
ranked with these weights:

| Signal | Score |
| --- | ---: |
| Same sub-category | 5 |
| Same main category | 3 |
| Same brand | 3 |
| Same material | 2 |
| Similar price (within 25%) | 2 |
| Shared tags | 1 each, maximum 3 |

In-stock products come first, then the score. The API returns at most four.

## Bonus

So far the rating breakdown is implemented: the detail page shows the average
rating, the number of reviews and a bar per star rating (5★ down to 1★), built
from the `reviews` table with one `GROUP BY` query.

The next ones I would add, in order of value for the effort:

- Sort reviews by most helpful (`?sort=helpful`), which reuses the
  `helpful_count` column.
- Search autocomplete with a prefix query and a debounced input.
- Typo tolerance with PostgreSQL `pg_trgm`, as a fallback for searches that
  return no rows, so exact matches keep their precision.
- Relevance ranking, so a match in the product name ranks above a match in the
  description.
- Filter counts that follow the current search, so a brand shows "Oakline (6)"
  for the current result set.
- Recently viewed products in `localStorage`.
- GitHub Actions that run the tests on every push.

## Data issues handled

- One product has no image, so the UI shows a placeholder.
- Missing or `null` attributes are treated as unknown and not stored as a value.
- Products without reviews keep a null rating and zero review count.
- Review bodies may be null.
- An invalid old price is retained but not shown as a sale price.
- Duplicate collection membership is removed during seeding.
- Draft and archived products, expired collections, and hidden collection
  products are excluded by API rules.

## Trade-offs and next steps

- Search is simple `ILIKE`; add full-text search, typo tolerance, and ranking.
- Add authentication and an admin interface for catalog editing.
- Add API integration tests and CI.
- Serve images directly from the API or object storage in production.
- Add caching and monitoring for a production deployment.

## Time spent

Approximately 12-13 hours.

## AI usage

Codex was used for code assistance, Docker configuration, and README writing.
The final code was reviewed before use.
