"use client";

import map from "lodash/map";
import { ChevronDown, SlidersHorizontal, X } from "lucide-react";
import { type FormEvent, type ReactNode, useEffect, useState } from "react";
import Button from "@/shared/components/ui/Button";
import type { Brand, CategoryNode } from "../../types/product";
import { parseOptionalNumber } from "../../utils";

const RATING_OPTIONS = [4, 3, 2, 1];

type FilterPatch = Record<string, string | null>;

type ProductFiltersProps = {
  categories: CategoryNode[];
  brands: Brand[];
  category?: string;
  selectedBrands: string[];
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
  inStock: boolean;
  hasFilters: boolean;
  onUpdate: (patch: FilterPatch) => void;
  onClear: () => void;
};

const choiceClass = (active: boolean) =>
  `flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm ${
    active
      ? "bg-navy font-bold text-white"
      : "font-semibold text-navy/70 hover:bg-dusk-50 hover:text-navy"
  }`;

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="border-t border-dusk-100 pt-5 first:border-0 first:pt-0">
      <h3 className="mb-3 text-sm font-bold text-navy">{title}</h3>
      {children}
    </section>
  );
}

export default function ProductFilters({
  categories,
  brands,
  category,
  selectedBrands,
  minPrice,
  maxPrice,
  minRating,
  inStock,
  hasFilters,
  onUpdate,
  onClear,
}: ProductFiltersProps) {
  const [minPriceText, setMinPriceText] = useState(minPrice?.toString() ?? "");
  const [maxPriceText, setMaxPriceText] = useState(maxPrice?.toString() ?? "");
  const [priceError, setPriceError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setMinPriceText(minPrice?.toString() ?? "");
  }, [minPrice]);

  useEffect(() => {
    setMaxPriceText(maxPrice?.toString() ?? "");
  }, [maxPrice]);

  function toggleBrand(slug: string) {
    const next = selectedBrands.includes(slug)
      ? selectedBrands.filter((selected) => selected !== slug)
      : [...selectedBrands, slug];
    onUpdate({ brand: next.length > 0 ? next.join(",") : null, page: null });
  }

  function applyPrice(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const min = parseOptionalNumber(minPriceText);
    const max = parseOptionalNumber(maxPriceText);

    if (minPriceText.trim() && min === undefined) {
      setPriceError("Minimum price must be a non-negative number.");
      return;
    }
    if (maxPriceText.trim() && max === undefined) {
      setPriceError("Maximum price must be a non-negative number.");
      return;
    }
    if (min !== undefined && max !== undefined && min > max) {
      setPriceError("Minimum price cannot be greater than maximum price.");
      return;
    }

    setPriceError(null);
    onUpdate({
      minPrice: min === undefined ? null : String(min),
      maxPrice: max === undefined ? null : String(max),
      page: null,
    });
  }

  return (
    <aside className="h-fit rounded-2xl border border-dusk-100 bg-white p-5 md:sticky md:top-20">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 md:hidden"
      >
        <span className="inline-flex items-center gap-2 text-sm font-extrabold uppercase tracking-widest text-navy/60">
          <SlidersHorizontal size={16} aria-hidden="true" />
          Filters
        </span>
        <ChevronDown
          size={18}
          aria-hidden="true"
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      <div className={`${open ? "block" : "hidden"} mt-5 md:mt-0 md:block`}>
        <div
          className={`mb-5 ${hasFilters ? "flex" : "hidden md:flex"} items-center justify-between gap-3`}
        >
          <h2 className="hidden text-sm font-extrabold uppercase tracking-widest text-navy/60 md:block">
            Filters
          </h2>
          {hasFilters && (
            <Button
              variant="ghost"
              onClick={onClear}
              className="ml-auto inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold"
            >
              <X size={13} aria-hidden="true" />
              Clear all
            </Button>
          )}
        </div>

        <div className="space-y-5">
          <Section title="Category">
            <div className="grid gap-1">
              <button
                type="button"
                aria-pressed={!category}
                onClick={() => onUpdate({ category: null, page: null })}
                className={choiceClass(!category)}
              >
                All products
              </button>

              {map(categories, (main) => (
                <div key={main.slug}>
                  <button
                    type="button"
                    aria-pressed={category === main.slug}
                    onClick={() =>
                      onUpdate({ category: main.slug, page: null })
                    }
                    className={choiceClass(category === main.slug)}
                  >
                    <span>{main.name}</span>
                    <span className="text-xs opacity-60">
                      {main.productCount}
                    </span>
                  </button>

                  {main.children.length > 0 && (
                    <div className="ml-3 mt-1 grid gap-1 border-l border-dusk-100 pl-3">
                      {map(main.children, (child) => (
                        <button
                          key={child.slug}
                          type="button"
                          aria-pressed={category === child.slug}
                          onClick={() =>
                            onUpdate({ category: child.slug, page: null })
                          }
                          className={choiceClass(category === child.slug)}
                        >
                          <span>{child.name}</span>
                          <span className="text-xs opacity-60">
                            {child.productCount}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>

          <Section title="Brand">
            <div className="grid max-h-64 gap-2 overflow-y-auto pr-1">
              {map(brands, (brand) => (
                <label
                  key={brand.slug}
                  className="flex items-center gap-3 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedBrands.includes(brand.slug)}
                    onChange={() => toggleBrand(brand.slug)}
                    className="size-4 shrink-0 accent-navy"
                  />
                  <span className="flex-1 font-semibold text-navy">
                    {brand.name}
                  </span>
                  <span className="text-xs text-navy/50">
                    {brand.productCount}
                  </span>
                </label>
              ))}
            </div>
          </Section>

          <Section title="Price">
            <form onSubmit={applyPrice} className="grid gap-2">
              <div className="flex items-center gap-2">
                <label htmlFor="min-price" className="sr-only">
                  Minimum price
                </label>
                <input
                  id="min-price"
                  type="number"
                  min="0"
                  step="0.01"
                  inputMode="decimal"
                  value={minPriceText}
                  onChange={(event) => setMinPriceText(event.target.value)}
                  placeholder="Min"
                  className="w-full rounded-lg border border-dusk-100 bg-white px-3 py-2 text-sm text-navy placeholder:text-navy/50 focus:border-dusk focus:outline-none focus:ring-2 focus:ring-dusk/30"
                />
                <span className="text-navy/40">–</span>
                <label htmlFor="max-price" className="sr-only">
                  Maximum price
                </label>
                <input
                  id="max-price"
                  type="number"
                  min="0"
                  step="0.01"
                  inputMode="decimal"
                  value={maxPriceText}
                  onChange={(event) => setMaxPriceText(event.target.value)}
                  placeholder="Max"
                  className="w-full rounded-lg border border-dusk-100 bg-white px-3 py-2 text-sm text-navy placeholder:text-navy/50 focus:border-dusk focus:outline-none focus:ring-2 focus:ring-dusk/30"
                />
              </div>

              <Button
                type="submit"
                variant="ghost"
                className="rounded-lg border border-dusk-100 bg-white px-3 py-2 text-sm font-semibold hover:bg-dusk-50"
              >
                Apply price
              </Button>

              {priceError && (
                <p className="text-xs font-semibold text-red-700">
                  {priceError}
                </p>
              )}
            </form>
          </Section>

          <Section title="Rating">
            <div className="grid gap-2">
              <label className="flex items-center gap-3 text-sm font-semibold text-navy/70">
                <input
                  type="radio"
                  name="min-rating"
                  checked={minRating === undefined}
                  onChange={() => onUpdate({ minRating: null, page: null })}
                  className="size-4 accent-navy"
                />
                Any rating
              </label>
              {map(RATING_OPTIONS, (rating) => (
                <label
                  key={rating}
                  className="flex items-center gap-3 text-sm font-semibold text-navy/70"
                >
                  <input
                    type="radio"
                    name="min-rating"
                    checked={minRating === rating}
                    onChange={() =>
                      onUpdate({ minRating: String(rating), page: null })
                    }
                    className="size-4 accent-navy"
                  />
                  {rating}★ & up
                </label>
              ))}
            </div>
          </Section>

          <Section title="Availability">
            <label className="flex items-center gap-3 text-sm font-semibold text-navy">
              <input
                type="checkbox"
                checked={inStock}
                onChange={(event) =>
                  onUpdate({
                    inStock: event.target.checked ? "true" : null,
                    page: null,
                  })
                }
                className="size-4 accent-navy"
              />
              In stock only
            </label>
          </Section>
        </div>
      </div>
    </aside>
  );
}
