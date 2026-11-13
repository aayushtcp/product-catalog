# Junior Full-Stack Developer

### Product Catalog: Database · REST API · Web Frontend

You'll build a small product catalog for a home and living shop: a database, an API on top of it, and a web frontend that uses the API. We want to see how you model data, design an API, build a UI, and package it so anyone can run it.

|               |                                                                          |
| ------------- | ------------------------------------------------------------------------ |
| **Time**      | About 10-12 hours of work. See [Time and scope](#time-and-scope) below.  |
| **Deadline**  | Sunday, 15 November 2026, 5:00 PM (Nepal Time)                           |
| **You get**   | `catalog.json` (the shop data) and `images/` (160 product images)        |
| **After**     | A 15-30 min video call: you show us the app and walk us through the code |

### Time and scope

The task is a bit bigger than 10-12 hours on purpose. We don't expect everything to be finished.

- Work in this order: **A → B → C → D → E**.
- When you reach about 12 hours, stop. Write in the README what is missing and how you would build it.
- A smaller app that works well is better than a bigger one that is half broken.

---

## Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Data reference](#3-data-reference)
4. [Business rules](#4-business-rules)
5. [Part A: Database and seed](#5-part-a-database-and-seed)
6. [Part B: REST API](#6-part-b-rest-api)
7. [Part C: Frontend](#7-part-c-frontend)
8. [Part D: Docker](#8-part-d-docker)
9. [Part E: Repository and README](#9-part-e-repository-and-readme)
10. [Part F: Deployment (optional)](#10-part-f-deployment-optional)
11. [Tech stack](#11-tech-stack)
12. [Bonus](#12-bonus)
13. [FAQ](#13-faq)
14. [Submission](#14-submission)

---

## 1. Overview

The shop sells rugs, lamps, furniture, candles and more. Its whole catalog is in one JSON file, plus a folder of product images. You build:

| Part | What                                                      | Required |
| ---- | --------------------------------------------------------- | -------- |
| A    | Database schema + seed script that imports `catalog.json` | Yes      |
| B    | REST API with search, filters, sorting and pagination     | Yes      |
| C    | Web frontend: product list, product detail, collections   | Yes      |
| D    | Docker setup: one command starts everything               | Yes      |
| E    | GitHub repository with a good README                      | Yes      |
| F    | Deployment                                                | Optional |

Each part can be built and tested on its own. Parts A-C don't need Docker. You add Docker in Part D.

---

## 2. Architecture

```
┌──────────────┐   HTTP / JSON   ┌──────────────┐      SQL / query     ┌──────────────┐
│   Frontend   │ ──────────────► │   REST API   │ ───────────────────► │   Database   │
│ React / Next │ ◄────────────── │ Node / Python│ ◄─────────────────── │ e.g. Postgres│
└──────────────┘                 └──────────────┘                      └──────────────┘
                                                                              ▲
                                        catalog.json ──► seed script ─────────┘
```

At the end (Part D), all three run as containers with `docker compose`.

---

## 3. Data reference

`catalog.json` has these parts:

| Key                   | Count | What it is                                                      |
| --------------------- | ----- | --------------------------------------------------------------- |
| `brands`              | 12    | Product brands                                                  |
| `categories`          | 19    | Two levels: 5 main categories, 14 sub-categories                |
| `collections`         | 8     | Hand-picked product lists, some only for a limited time         |
| `products`            | 120   | Products with status, tags, features, attributes and images     |
| `products[].variants` | 336   | Color/size versions of a product, each with its own price and stock |
| `reviews`             | 933   | Customer reviews, linked by `productId`                         |

### Field reference

**Brand**

| Field     | Type   | Notes          |
| --------- | ------ | -------------- |
| `id`      | string | e.g. `b06`     |
| `slug`    | string | e.g. `oakline` |
| `name`    | string |                |
| `country` | string |                |

**Category**

| Field      | Type           | Notes                                                                    |
| ---------- | -------------- | ------------------------------------------------------------------------ |
| `id`       | string         |                                                                          |
| `slug`     | string         |                                                                          |
| `name`     | string         |                                                                          |
| `parentId` | string \| null | `null` means it's a main category. Products always link to a sub-category. |

**Collection**

| Field                               | Type                    | Notes                 |
| ----------------------------------- | ----------------------- | --------------------- |
| `id`, `slug`, `name`, `description` | string                  |                       |
| `isActive`                          | boolean                 |                       |
| `startsAt`, `endsAt`                | ISO 8601 string \| null | `null` means no limit |
| `productIds`                        | string[]                |                       |

**Product**

| Field                               | Type                                    | Notes                                                                    |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------------------------------ |
| `id`, `slug`, `name`, `description` | string                                  |                                                                          |
| `brandId`                           | string                                  | → `brands[].id`                                                          |
| `categoryId`                        | string                                  | → `categories[].id` (a sub-category)                                     |
| `status`                            | `"active"` \| `"draft"` \| `"archived"` |                                                                          |
| `tags`                              | string[]                                |                                                                          |
| `features`                          | string[]                                | Short selling points for the detail page, e.g. `"Dimmable"`              |
| `attributes`                        | object                                  | Product details. See [Attributes](#attributes) below.                    |
| `images`                            | `{ url, alt }[]`                        | `url` is a relative path into the `images/` folder. Can be empty.        |
| `variants`                          | Variant[]                               | See below                                                                |
| `ratingAverage`                     | number \| null                          | `null` means no reviews yet                                              |
| `reviewCount`                       | number                                  |                                                                          |
| `views`, `salesCount`               | number                                  |                                                                          |
| `createdAt`, `updatedAt`            | ISO 8601 string (UTC)                   |                                                                          |

#### Attributes

Every product has the keys `material`, `origin` and `care`. Other keys depend on the category:

| Category                    | Possible keys                                                      |
| --------------------------- | ------------------------------------------------------------------ |
| Rugs                        | `construction`, `pileHeightMm`, `washable`                         |
| Cushions, Throws & Blankets | `washable`, `washTempC`, `fillMaterial`                            |
| Seating, Tables, Storage    | `assemblyRequired`, `warrantyYears`, `maxLoadKg`                   |
| Lamps and pendant lights    | `bulbType`, `maxWatt`, `bulbIncluded`, `dimmable`, `cableLengthCm` |
| Vases, Wall Art             | `waterproof`, `readyToHang`                                        |
| Candles                     | `burnTimeHours`, `scented`                                         |
| Tableware                   | `dishwasherSafe`, `microwaveSafe`                                  |

Any product can also have `weightKg`.

**Missing and `null` mean the same thing.** A key can be left out, or it can be there with the value `null`. Both mean "we don't know this value", and your app should treat them the same way.

How you store these changing keys (extra columns, a JSON column, a key-value table, …) is up to you. Explain your choice in the README.

**Variant** (inside a product)

| Field            | Type              | Notes                                         |
| ---------------- | ----------------- | --------------------------------------------- |
| `sku`            | string            | Unique                                        |
| `options`        | `{ color, size }` | Not every color/size combination exists       |
| `price`          | number            | EUR                                           |
| `compareAtPrice` | number \| null    | Old price, see rule R5                        |
| `stock`          | number            | `0` means sold out                            |

**Review**

| Field              | Type            | Notes                                          |
| ------------------ | --------------- | ---------------------------------------------- |
| `id`               | string          |                                                |
| `productId`        | string          | → `products[].id`                              |
| `rating`           | number          | 1-5                                            |
| `title`            | string          |                                                |
| `body`             | string \| null  |                                                |
| `verifiedPurchase` | boolean         |                                                |
| `helpfulCount`     | number          | How many shoppers marked the review as helpful |
| `createdAt`        | ISO 8601 string |                                                |

### Example product (shortened)

```json
{
  "id": "p001",
  "slug": "shaggy-diamond-rug",
  "name": "Shaggy Diamond Rug",
  "brandId": "b01",
  "categoryId": "c11",
  "status": "active",
  "tags": ["wool", "shaggy", "handwoven"],
  "attributes": {
    "material": "Wool",
    "origin": "Morocco",
    "care": "Vacuum regularly ...",
    "construction": "handwoven",
    "pileHeightMm": 12,
    "washable": false
  },
  "features": ["Handwoven", "Pile height 12 mm", "Made in Morocco"],
  "images": [
    { "url": "images/p001-1.jpg", "alt": "Shaggy Diamond Rug - product photo" }
  ],
  "variants": [
    {
      "sku": "P001-CREAM-1",
      "options": { "color": "Cream", "size": "120 x 170 cm" },
      "price": 349.0,
      "compareAtPrice": null,
      "stock": 2
    }
  ],
  "ratingAverage": 4.1,
  "reviewCount": 18,
  "createdAt": "2025-02-22T10:00:00Z"
}
```

### Images

The product images are in the `images/` folder next to `catalog.json` (e.g. `images/p001-1.jpg`, 680 × 680 px). They are AI-generated, and you can put them in your repository.

Your app must serve the images itself, for example as static files from the API (`GET /images/p001-1.jpg`) or from the frontend's public folder. The API should return a URL the browser can load directly. Please don't upload them to an external image host.

### Data quality

> **Please don't change `catalog.json`.**
>
> Like real shop data, the file is **not perfectly clean**. Some values are `null` or missing, some lists are empty, and a few things don't add up. Finding and handling these is part of the task. In your README, write what you found and how you handled it (in the seed, the API or the UI).

---

## 4. Business rules

These rules apply to **every** endpoint and page.

| ID     | Rule                                                                                                                                                       | Example                                                                                  |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **R1** | Only products with `status: "active"` are visible. `draft` and `archived` products never show up in lists, search, collections, counts or similar products. | "Extendable Dining Table" is a draft → hidden everywhere, and its detail URL returns `404`. |
| **R2** | A product's list price is its **lowest variant price**. Price filters and price sorting use this value.                                                    | Variants at €349 / €559 / €839 → the list shows "from €349".                              |
| **R3** | A product is **in stock** if at least one variant has `stock > 0`.                                                                                         |                                                                                          |
| **R4** | A collection is visible only if `isActive = true` **and** today is between `startsAt` and `endsAt`. A `null` date means no limit on that side.             | "Summer Terrace" ended on 31 August → hidden.                                            |
| **R5** | A product is on sale only if `compareAtPrice > price`. Otherwise, don't show an old price.                                                                  |                                                                                          |

---

## 5. Part A: Database and seed

### Requirements

- Design a schema for the data. Which entities get their own table (or collection) and how they relate is up to you.
- Write a seed script (or migration) that imports `catalog.json`.
- The seed must be **idempotent**: running it twice must not create duplicates.
- Add indexes for the columns your filters and sorting use. List them in the README with one line on why each one helps.

### Done when

- [ ] The seed runs with one command, e.g. `npm run seed` or `python manage.py seed`
- [ ] After seeding, the database has 120 products, 336 variants and 933 reviews
- [ ] Running the seed again doesn't change these numbers

Docker isn't needed for this part. A local database is fine. In Part D, you make the seed run automatically.

---

## 6. Part B: REST API

### Endpoints

You can change this contract if you have a better design. Just explain why in the README.

| Method | Path                          | Description                                                        |
| ------ | ----------------------------- | ------------------------------------------------------------------ |
| `GET`  | `/api/products`               | Product list with search, filters, sorting, pagination             |
| `GET`  | `/api/products/:slug`         | Product detail: brand, category path, attributes, features, images, variants |
| `GET`  | `/api/products/:slug/reviews` | Reviews of a product, newest first, paginated                      |
| `GET`  | `/api/products/:slug/similar` | Up to 4 similar products                                           |
| `GET`  | `/api/categories`             | Category tree with the number of products in each category         |
| `GET`  | `/api/brands`                 | Brands with their product count                                    |
| `GET`  | `/api/collections`            | Visible collections (R4)                                           |
| `GET`  | `/api/collections/:slug`      | One collection with its products, paginated                        |

All counts only include visible products (R1). A main category's count includes its sub-categories.

### `GET /api/products` query parameters

All parameters are optional, and they can be combined.

| Parameter   | Type         | Example                     | Behavior                                                                                                                                                                                                                                           |
| ----------- | ------------ | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `q`         | string       | `q=oak dining`              | Searches name, description, brand name, category name, material and tags. Not case-sensitive. Extra spaces are ignored. Partial words match (`handwov` → "handwoven"). With several words, a product must match **all** of them. |
| `category`  | slug         | `category=lighting`         | A main category includes all of its sub-categories.                                                                                                                                                                                                |
| `brand`     | slug list    | `brand=oakline,north-house` | Comma-separated. Matches any of the listed brands.                                                                                                                                                                                                 |
| `minPrice`  | number       | `minPrice=100`              | Inclusive, based on R2.                                                                                                                                                                                                                            |
| `maxPrice`  | number       | `maxPrice=300`              | Inclusive, based on R2.                                                                                                                                                                                                                            |
| `inStock`   | boolean      | `inStock=true`              | Only in-stock products (R3).                                                                                                                                                                                                                       |
| `minRating` | number (1-5) | `minRating=4`               | Leaves out products without a rating.                                                                                                                                                                                                              |
| `sort`      | enum         | `sort=price_asc`            | `price_asc` · `price_desc` · `newest` · `rating` (unrated last) · `popular` (by `salesCount`)                                                                                                                                                      |
| `page`      | integer ≥ 1  | `page=2`                    | Default `1`                                                                                                                                                                                                                                        |
| `limit`     | integer 1-50 | `limit=12`                  | Default `12`                                                                                                                                                                                                                                       |

**Example request**

```http
GET /api/products?q=candle&category=decor&inStock=true&sort=price_asc&page=1&limit=12
```

**Example response (`200 OK`)**

```json
{
  "items": [
    {
      "id": "p043",
      "slug": "taper-candles-set-of-6",
      "name": "Taper Candles (Set of 6)",
      "brand": { "slug": "north-house", "name": "North House" },
      "category": { "slug": "candles", "name": "Candles" },
      "price": 12.99,
      "compareAtPrice": null,
      "inStock": true,
      "ratingAverage": 3.7,
      "reviewCount": 18,
      "image": {
        "url": "http://localhost:4000/images/p043-1.jpg",
        "alt": "Taper Candles (Set of 6) - product photo"
      }
    }
  ],
  "page": 1,
  "limit": 12,
  "total": 7,
  "totalPages": 1
}
```

### `GET /api/products/:slug` example response (shortened)

```json
{
  "id": "p001",
  "slug": "shaggy-diamond-rug",
  "name": "Shaggy Diamond Rug",
  "description": "...",
  "brand": { "slug": "desert-weavers", "name": "Desert Weavers" },
  "categoryPath": [
    { "slug": "home-textiles", "name": "Home Textiles" },
    { "slug": "rugs", "name": "Rugs" }
  ],
  "attributes": { "material": "Wool", "origin": "Morocco", "care": "..." },
  "features": ["Handwoven", "Pile height 12 mm", "Made in Morocco"],
  "images": [{ "url": "...", "alt": "..." }],
  "variants": [
    {
      "sku": "P001-CREAM-1",
      "color": "Cream",
      "size": "120 x 170 cm",
      "price": 349,
      "compareAtPrice": null,
      "stock": 2
    }
  ],
  "ratingAverage": 4.1,
  "reviewCount": 18
}
```

### Errors

Use one error shape for every error, for example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "minPrice must be a number",
    "details": [{ "field": "minPrice", "value": "abc" }]
  }
}
```

| Status                      | When                                                                                                  |
| --------------------------- | ----------------------------------------------------------------------------------------------------- |
| `400 Bad Request`           | Invalid input: `minPrice=abc`, `minPrice > maxPrice`, unknown `sort`, unknown `category`, `limit=0` … |
| `404 Not Found`             | Unknown slug, hidden product (R1), hidden collection (R4)                                             |
| `500 Internal Server Error` | Only for unexpected errors. Bad input must never cause a `500` or a crash.                            |

### Technical requirements

1. **Let the database do the work.** Filtering, sorting and pagination happen in the database query. Loading every row and filtering in code is not accepted.
2. **Stable order.** Several products have the same price. Add a second sort key (e.g. `id`) so a product never shows up on two pages.
3. **Safe queries.** Never build queries by gluing user input into a string. Use parameterized queries or an ORM / query builder.
4. **Similar products.** Score other products by how much they have in common with this one, for example the same sub-category, same main category, same brand, same material, shared tags or a similar price. Return the top 4.
   - never the product itself
   - no duplicates
   - only visible products (R1)
   - sold-out products: put them last or leave them out (your choice)
   - explain the scoring and weights in the README
5. **Tests.** A few automated tests for the core logic, for example input validation, the business rules or the similarity score. Around 5-10 good tests is plenty.

### Done when

- [ ] All endpoints above return the right data and follow R1-R5
- [ ] All query parameters work in any combination
- [ ] Invalid input returns `400` with the error shape above
- [ ] Paging through all results returns every product exactly once
- [ ] Tests run with one command (e.g. `npm test` or `pytest`)

---

## 7. Part C: Frontend

### Product list page

- Search box
- Category navigation (main categories with their sub-categories)
- Filters: brand (pick several), price range, in stock only, minimum rating
- Sort dropdown
- Pagination
- **State in the URL:** search, filters, sort and page live in the query string. Opening a copied link shows the same results, and the browser's back button works.
- **Loading, error and empty states**
- **Product card:** image, name, brand, price ("from €…" when variant prices differ), crossed-out old price (R5), rating, "Sold out" badge

### Product detail page

- Breadcrumb, e.g. _Home Textiles › Rugs_
- Image gallery, with a placeholder when there are no images
- Name, brand, description, features (as a list) and attributes. Only show attributes that have a value, with readable labels (e.g. `pileHeightMm: 12` → "Pile height: 12 mm").
- **Variant picker:** the shopper picks a color and a size. Price, old price, stock and SKU update to match.
  - combinations that don't exist can't be picked
  - sold-out variants are shown as unavailable
- Stock label: "In stock", "Only X left" (1-2 pieces) or "Sold out"
- Reviews: average, count, and a list with pagination or a "Load more" button
- Similar products

### Collections

- A page listing the visible collections
- One page per collection with its products

### General

- Works on mobile and desktop
- Prices shown in EUR (e.g. `€29.90`)
- Never show `null`, `undefined` or `NaN` anywhere

The design doesn't need to be fancy. Clean, consistent and easy to use is what we're looking for.

### Done when

- [ ] A shopper can search, filter, sort, change pages and share the URL
- [ ] A shopper can open a product, pick a variant and see the right price and stock
- [ ] Missing data (images, rating, review text, attributes) is handled cleanly
- [ ] All pages work at 375 px width

---

## 8. Part D: Docker

Now package what you built so anyone can run it with one command:

```bash
docker compose up --build
```

This starts the database, the API and the frontend, and runs the seed automatically.

**Configuration:**

- Read configuration from environment variables.
- The stack must start **without** a `.env` file. Put safe local defaults in `docker-compose.yml`, for example `${POSTGRES_PASSWORD:-postgres}`.
- Commit a `.env.example` that lists every variable. A `.env` file is only for overriding the defaults.
- Never commit real secrets or your `.env` file.

### Done when

- [ ] A fresh clone + `docker compose up --build` (nothing else) gives a working app with data
- [ ] Starting it a second time doesn't duplicate the data
- [ ] The README lists the URLs and ports for the frontend and the API

---

## 9. Part E: Repository and README

### Repository

- A public GitHub repository (or a private one that we have access to)
- Small, meaningful commits that show how you worked. One big "initial commit" with everything in it isn't a good sign.
- Don't commit `node_modules`, build output, database files or `.env`

Suggested structure (not required):

```
.
├── backend/
│   ├── src/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   └── Dockerfile
├── data/
│   ├── catalog.json
│   └── images/
├── docker-compose.yml
├── .env.example
└── README.md
```

### Your README should cover

1. **Setup**: how to run it with Docker
2. **Tech stack**: what you chose and why
3. **Database schema**: tables/collections, how they relate, and your indexes (a diagram or a list is fine)
4. **API docs**: endpoints, parameters, example responses, error shape
5. **Search**: how it works and where it falls short
6. **Similar products**: the scoring and the weights
7. **Data issues**: what you found in `catalog.json` and how you handled it
8. **Trade-offs and next steps**: what's missing, and what you'd improve with more time
9. **Time spent**: roughly how many hours
10. **AI usage**: which tools you used, and for what

---

## 10. Part F: Deployment (optional)

- **Next.js:** Vercel's free tier is the easiest option. You'll also need a hosted database, e.g. a free Neon or Supabase Postgres.
- **Separate backend** (Express, Django, FastAPI, …): a working Docker setup is enough.
- Skipping deployment doesn't count against you.

---

## 11. Tech stack

Use what you know best.

| Layer    | Options                                                                                 |
| -------- | --------------------------------------------------------------------------------------- |
| Frontend | React (Vite) or Next.js                                                                 |
| Backend  | Node.js (Express, Fastify, NestJS), Python (Django, FastAPI), or Next.js Route Handlers |
| Database | PostgreSQL (preferred), MongoDB or SQLite                                               |
| Language | JavaScript or TypeScript (welcome, not required), Python                                |

If you build everything in Next.js, keep a clear API layer. No database queries inside React components.

---

## 12. Bonus

Only after Parts A-E work. One bonus done well is worth more than five done badly.

- Sort reviews by most helpful (`?sort=helpful`, using `helpfulCount`)
- Search autocomplete
- Typo tolerance (`candel` → "candle"), e.g. with PostgreSQL `pg_trgm`
- Relevance ranking (a match in the name ranks above a match in the description)
- Filter counts that update with the current search, e.g. "Oakline (6)"
- Rating breakdown on the detail page (5★ … 1★)
- "Recently viewed" products using `localStorage`
- GitHub Actions that run your tests
- Caching for frequent requests
- OpenAPI / Swagger docs

---

## 13. FAQ

**Can I use AI tools (ChatGPT, Copilot, Claude, Cursor, …)?**
Yes. But you need to understand every line you hand in. In the call, we'll ask you to explain your code.

**Can I change the API design?**
Yes, if you have a good reason. Write it in the README.

**Something is unclear. What should I do?**
Reply to the email this task came with. If you can't wait for an answer, make a sensible choice and note it in the README.

**I'm running out of time. What matters most?**
Parts A, B and C, in that order, then D and E. Stop at about 12 hours and list what's missing in the README.

---

## 14. Submission

Reply to the email this task came with and include:

- [ ] The link to your GitHub repository
- [ ] A deployment URL (optional)
- [ ] 2-4 screenshots or a short screen recording (max. 3 minutes)

Good luck - we're looking forward to seeing what you build.
