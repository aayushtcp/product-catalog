"use client";

import map from "lodash/map";
import { Search } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { type SubmitEvent, useEffect, useState } from "react";
import Button from "@/shared/components/ui/Button";
import { useGetBrands } from "../hooks/useGetBrands";
import { useGetCategories } from "../hooks/useGetCategories";
import { useGetProducts } from "../hooks/useGetProducts";
import type { ProductSort } from "../types/product";
import {
  getPageNavigation,
  getPaginationLabel,
  PAGE_SIZE,
  parseOptionalNumber,
  parsePage,
  parseSlugs,
} from "../utils";
import ProductCard from "./ui/ProductCard";
import ProductFilters from "./ui/ProductFilters";

const SKELETON_ITEMS = [1, 2, 3, 4, 5, 6, 7, 8];

const SORT_OPTIONS: { value: ProductSort; label: string }[] = [
  { value: "newest", label: "Newest" },
  { value: "price_asc", label: "Price: low to high" },
  { value: "price_desc", label: "Price: high to low" },
  { value: "rating", label: "Rating" },
  { value: "popular", label: "Popular" },
];

export default function ProductsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const q = searchParams.get("q") ?? "";
  const category = searchParams.get("category") ?? undefined;
  const brandParam = searchParams.get("brand");
  const selectedBrands = parseSlugs(brandParam);
  const minPrice = parseOptionalNumber(searchParams.get("minPrice"));
  const maxPrice = parseOptionalNumber(searchParams.get("maxPrice"));
  const minRatingValue = parseOptionalNumber(searchParams.get("minRating"));
  const minRating =
    minRatingValue !== undefined && minRatingValue >= 1 && minRatingValue <= 5
      ? minRatingValue
      : undefined;
  const sortParam = searchParams.get("sort");
  const sort: ProductSort = SORT_OPTIONS.some((o) => o.value === sortParam)
    ? (sortParam as ProductSort)
    : "newest";
  const page = parsePage(searchParams.get("page"));
  const inStock = searchParams.get("inStock") === "true";

  const [text, setText] = useState(q);

  useEffect(() => {
    setText(q);
  }, [q]);

  const { data: categories } = useGetCategories();
  const { data: brands } = useGetBrands();
  const { data, isPending, isError, error, refetch } = useGetProducts({
    q: q || undefined,
    category,
    brand: selectedBrands.length > 0 ? selectedBrands.join(",") : undefined,
    minPrice,
    maxPrice,
    sort,
    page,
    inStock: inStock || undefined,
    minRating,
    limit: PAGE_SIZE,
  });

  function update(patch: Record<string, string | null>) {
    const next = new URLSearchParams(searchParams.toString());
    for (const [key, value] of Object.entries(patch)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    const query = next.toString();
    router.push(query ? `${pathname}?${query}` : pathname);
  }

  function onSearch(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    update({ q: text.trim() || null, page: null });
  }

  const hasFilters = Boolean(
    q ||
      category ||
      brandParam ||
      searchParams.has("minPrice") ||
      searchParams.has("maxPrice") ||
      searchParams.has("minRating") ||
      inStock ||
      sortParam,
  );
  const { previous, next } = getPageNavigation(page, data?.totalPages ?? 0);

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-10">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-navy/60">
            Shop
          </p>
          <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-navy md:text-4xl">
            Products
          </h1>
        </div>

        <form onSubmit={onSearch} className="flex w-full gap-2 md:max-w-md">
          <label htmlFor="product-q" className="sr-only">
            Search products
          </label>
          <input
            id="product-q"
            type="search"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Search products"
            className="w-full rounded-full border border-dusk-100 bg-white px-4 py-2 text-navy placeholder:text-navy/50 focus:border-dusk focus:outline-none focus:ring-2 focus:ring-dusk/30"
          />
          <Button
            type="submit"
            variant="primary"
            className="inline-flex items-center gap-2 rounded-full px-4 py-2"
          >
            <Search size={16} aria-hidden="true" />
            Search
          </Button>
        </form>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-[16rem_minmax(0,1fr)] md:gap-8">
        <ProductFilters
          categories={categories ?? []}
          brands={brands ?? []}
          category={category}
          selectedBrands={selectedBrands}
          minPrice={minPrice}
          maxPrice={maxPrice}
          minRating={minRating}
          inStock={inStock}
          hasFilters={hasFilters}
          onUpdate={update}
          onClear={() => router.push(pathname)}
        />

        <div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-navy/70">
              {isPending
                ? "Loading products…"
                : data
                  ? `${data.total} ${data.total === 1 ? "product" : "products"}`
                  : "Products"}
            </p>

            <label className="flex items-center gap-2 text-sm font-semibold text-navy">
              Sort
              <select
                value={sort}
                onChange={(event) =>
                  update({ sort: event.target.value, page: null })
                }
                className="rounded-lg border border-dusk-100 bg-white px-3 py-1.5 text-navy focus:border-dusk focus:outline-none focus:ring-2 focus:ring-dusk/30"
              >
                {map(SORT_OPTIONS, (option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {isPending && (
            <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
              {map(SKELETON_ITEMS, (item) => (
                <div
                  key={item}
                  className="aspect-3/4 animate-pulse rounded-2xl bg-dusk-100"
                />
              ))}
            </div>
          )}

          {isError && (
            <div className="mt-6 rounded-2xl border border-dusk-100 bg-white p-6">
              <p className="font-semibold text-navy">
                {error instanceof Error
                  ? error.message
                  : "Could not load products."}
              </p>
              <Button
                variant="primary"
                onClick={() => refetch()}
                className="mt-3 rounded-full px-4 py-2"
              >
                Try again
              </Button>
            </div>
          )}

          {!isPending && !isError && data && data.items.length === 0 && (
            <div className="mt-6 rounded-2xl border border-dusk-100 bg-white p-6">
              <p className="font-semibold text-navy">No products found.</p>
              <p className="mt-1 text-navy/70">
                Try a different search or clear the filters.
              </p>
            </div>
          )}

          {!isPending && !isError && data && data.items.length > 0 && (
            <>
              <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                {map(data.items, (product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              <div className="mt-8 flex items-center justify-between gap-4 border-t border-dusk-100 pt-6">
                <Button
                  variant="ghost"
                  disabled={previous === null}
                  onClick={() => update({ page: String(previous) })}
                  className="rounded-full border border-dusk-100 bg-white px-4 py-2 font-semibold disabled:opacity-40"
                >
                  Previous
                </Button>
                <span className="text-sm text-navy/70">
                  {getPaginationLabel(page, data.totalPages, data.total)}
                </span>
                <Button
                  variant="ghost"
                  disabled={next === null}
                  onClick={() => update({ page: String(next) })}
                  className="rounded-full border border-dusk-100 bg-white px-4 py-2 font-semibold disabled:opacity-40"
                >
                  Next
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
