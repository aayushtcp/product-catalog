"use client";

import map from "lodash/map";
import { Search, X } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { type SubmitEvent, useEffect, useState } from "react";
import Button from "@/shared/components/ui/Button";
import { useGetProducts } from "../hooks/useGetProducts";
import type { ProductSort } from "../types/product";
import {
  getPageNavigation,
  getPaginationLabel,
  PAGE_SIZE,
  parsePage,
} from "../utils";
import ProductCard from "./ui/ProductCard";

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

  const { data, isPending, isError, refetch } = useGetProducts({
    q: q || undefined,
    category,
    sort,
    page,
    inStock: inStock || undefined,
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

  const hasFilters = Boolean(q || category || inStock || sortParam);
  const { previous, next } = getPageNavigation(page, data?.totalPages ?? 0);

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-10">
      <h1 className="text-3xl font-extrabold tracking-tight text-navy md:text-4xl">
        Products
      </h1>

      <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
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

        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm font-semibold text-navy">
            <input
              type="checkbox"
              checked={inStock}
              onChange={(event) =>
                update({
                  inStock: event.target.checked ? "true" : null,
                  page: null,
                })
              }
              className="size-4 accent-navy"
            />
            In stock only
          </label>

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

          {hasFilters && (
            <Button
              variant="ghost"
              onClick={() => router.push(pathname)}
              className="inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-sm font-semibold"
            >
              <X size={14} aria-hidden="true" />
              Clear
            </Button>
          )}
        </div>
      </div>

      {category && (
        <p className="mt-4 text-sm text-navy/70">
          Category: <span className="font-semibold text-navy">{category}</span>
        </p>
      )}

      {isPending && (
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          {map(SKELETON_ITEMS, (item) => (
            <div
              key={item}
              className="aspect-3/4 animate-pulse rounded-2xl bg-dusk-100"
            />
          ))}
        </div>
      )}

      {isError && (
        <div className="mt-8 rounded-2xl border border-dusk-100 bg-white p-6">
          <p className="font-semibold text-navy">Could not load products.</p>
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
        <div className="mt-8 rounded-2xl border border-dusk-100 bg-white p-6">
          <p className="font-semibold text-navy">No products found.</p>
          <p className="mt-1 text-navy/70">
            Try a different search or clear the filters.
          </p>
        </div>
      )}

      {!isPending && !isError && data && data.items.length > 0 && (
        <>
          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
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
  );
}
