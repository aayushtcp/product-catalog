# Product Catalog

A small home-and-living product catalog built from `data/catalog.json` and the
images in `data/images/`.

**Status:** Part A (database and seed) is implemented. Parts B–E are planned.

---

## Part A: Database and seed

### Tech stack

- PostgreSQL
- Python 3
- SQLAlchemy 2 (async) with the `psycopg` driver

The database schema is managed by Alembic. Running the seed executes
`alembic upgrade head` before importing data, so a fresh database gets its
schema from the migrations in `api/src/alembic/versions/`.

### Local setup

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp template.env .env
# fill in the database values in .env if your local Postgres differs

cd src
python -m seed
```

The seed command is:

```bash
cd api/src
python -m seed
```

It connects to the database configured in `api/.env`. If the target database does
not exist, the seed connects to the `postgres` database and creates it.

Default local database settings in `api/.env`:

```text
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=product_catalog
```

### What the seed does

1. Reads `CATALOG_JSON_PATH` (default: `../data/catalog.json`).
2. Validates IDs, slugs, SKUs and foreign-key references.
3. Cleans the data in memory without modifying `catalog.json`.
4. Creates the database if needed and applies Alembic migrations.
5. Upserts rows inside a single transaction.
6. Replaces derived rows (`product_images`, `collection_products`) exactly.
7. Logs warnings for data issues and prints final row counts.

Running the seed twice is safe. Expected counts after either run:

| Table | Count |
| --- | ---: |
| `brands` | 12 |
| `categories` | 19 |
| `products` | 120 |
| `variants` | 336 |
| `reviews` | 933 |
| `collections` | 8 |
| `product_images` | 160 |
| `collection_products` | 85 |

To verify manually:

```bash
cd api/src
python -m seed
python -m seed

psql -h localhost -U postgres -d product_catalog -c \
  "select
     (select count(*) from products) as products,
     (select count(*) from variants) as variants,
     (select count(*) from reviews) as reviews;"
```

Expected result:

```text
 products | variants | reviews
----------+----------+---------
      120 |      336 |     933
```

### Schema

```text
brands ──< products >── categories (self-referencing: parent_id)
              │
              ├──< variants
              ├──< product_images
              ├──< reviews
              └──< collection_products >── collections
```

| Table | Key columns |
| --- | --- |
| `brands` | `id` PK, `slug` unique, `name`, `country` |
| `categories` | `id` PK, `slug` unique, `name`, `parent_id` self-FK (nullable) |
| `products` | `id` PK, `slug` unique, `name`, `description`, `brand_id` FK, `category_id` FK, `status`, `tags TEXT[]`, `features TEXT[]`, `attributes JSONB`, `rating_average`, `review_count`, `views`, `sales_count`, `min_price`, `in_stock`, `created_at`, `updated_at` |
| `variants` | `id` PK, `product_id` FK, `sku` unique, `color`, `size`, `price`, `compare_at_price`, `stock`; unique `(product_id, color, size)` |
| `product_images` | `id` PK, `product_id` FK, `url`, `alt`, `position`; unique `(product_id, position)` |
| `reviews` | `id` PK, `product_id` FK, `rating`, `title`, `body`, `verified_purchase`, `helpful_count`, `created_at` |
| `collections` | `id` PK, `slug` unique, `name`, `description`, `is_active`, `starts_at`, `ends_at` |
| `collection_products` | composite PK `(collection_id, product_id)` |

### Design choices

- **JSON IDs stay as primary keys.** IDs such as `p001` and `b01` are stable and
  unique, so the seed can upsert directly without mapping generated numbers back
  to JSON IDs. Variants and images have no ID in the JSON, so the seed derives
  stable string IDs for them (`p001-v0`, `p001-i0`).
- **`product_images` is a separate table.** The data has 160 image references,
  41 products have more than one image, and one product has none. A separate
  table represents "zero or many" naturally, and `position` preserves gallery
  order.
- **`tags` and `features` are `TEXT[]`.** Both are plain lists of strings with
  no further structure. Postgres arrays fit, and `tags` can use a GIN index.
- **Varying attributes live in `JSONB`.** Attribute keys depend on the category,
  and new keys should not require a schema migration. Keys with `null` values are
  removed during seeding because the assignment treats missing and `null` as the
  same thing.
- **`min_price` and `in_stock` are denormalized.** R2 defines the list price as
  the lowest variant price, and R3 defines in-stock as at least one variant with
  stock. Computing these during seeding makes price filtering, price sorting and
  the in-stock filter simple indexed queries.
- **`rating_average` and `review_count` are denormalized.** They match the actual
  reviews in the source data. In a live shop they would be updated whenever a
  review changes.
- **Money uses `NUMERIC(10,2)`.** Prices never use floating point.
- **Dates use `TIMESTAMPTZ`.** The JSON uses UTC strings ending in `Z`.
- **Database checks:** `stock >= 0`, `price >= 0`, `rating BETWEEN 1 AND 5`,
  and `status IN ('active', 'draft', 'archived')`.

### Idempotency

The seed uses upserts:

| Table | Conflict key |
| --- | --- |
| `brands`, `categories`, `products`, `collections`, `reviews` | `id` |
| `variants` | `sku` |
| `product_images` | table is cleared and reinserted each run |
| `collection_products` | table is cleared and reinserted each run |

Known limitation: a plain upsert does not delete top-level rows that disappeared
from the JSON (for example, a product removed from the file). Derived tables are
rebuilt exactly each run. For this task the limitation is acceptable; a full sync
would delete rows whose IDs are no longer present in the JSON.

### Indexes

| Index | Why it helps |
| --- | --- |
| `products.slug` unique | Product detail lookup by slug. |
| `products.status` partial where active | R1 filters almost every request to active products. |
| `products.category_id` | Category filtering and category product counts. |
| `products.brand_id` | Brand filtering and brand product counts. |
| `products.min_price` | R2 price range filters and price sorting. |
| `products.in_stock` partial where true | R3 in-stock filtering. |
| `products.created_at DESC` | `sort=newest`. |
| `products.rating_average DESC NULLS LAST` | `sort=rating`, with unrated products last. |
| `products.sales_count DESC` | `sort=popular`. |
| `products.tags` GIN | Tag search and overlap filters. |
| `products.attributes` GIN (`jsonb_path_ops`) | Attribute lookups such as material. |
| `reviews(product_id, created_at DESC)` | Product reviews newest first with pagination. |
| `reviews(product_id, rating)` | Rating breakdown queries. |
| `categories.parent_id` | Building the category tree. |
| `collections(is_active, starts_at, ends_at)` partial where active | R4 visible-collection queries. |
| `collection_products(product_id)` | Reverse collection lookups. |
| `variants.sku` unique | Variant lookup and seed upsert key. |
| `variants(product_id, color, size)` unique | Variant picker and product detail lookups. |
| `product_images(product_id, position)` unique | Gallery order and image lookup. |
| Brand/category/collection `slug` unique | Lookup by slug in the API. |

### Data issues found and how they are handled

| Issue | Handling |
| --- | --- |
| `p030` has no images | Imported with zero image rows; the future UI will show a placeholder. |
| 50 null `care`, 3 null `fillMaterial`, 2 null `burnTimeHours` | Null attribute keys are dropped during seeding. |
| 19 products have no rating | `rating_average` stays `NULL`; `review_count` is `0`. |
| 68 reviews have a null body | `reviews.body` stays `NULL`. |
| `p009 / P009-EMERAL-1` has `compareAtPrice = 34` and `price = 39` | Stored as-is; R5 ignores a `compareAtPrice` that is not greater than `price`. |
| `col05` lists `p012` twice | Duplicate collection membership is removed during seeding. |
| 4 non-active products (2 draft, 2 archived) | All 120 products are imported; R1 hides them at query time. |
| Some collections contain hidden products | Memberships are imported; R1 filters hidden products at query time. |
| `summer-terrace` has already ended | Imported; R4 hides it at query time. |
| `pg_trgm` is not available locally | Search will use `ILIKE` instead of trigram indexes. |

### Seed tests

The cleaning logic has unit tests that do not need a database:

```bash
cd api/src
pytest tests/test_seed.py
```
