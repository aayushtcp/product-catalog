"use client";

import map from "lodash/map";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import ProductImage from "@/shared/components/ui/ProductImage";
import { formatPrice } from "@/shared/utils";
import { useGetProductDetails } from "../hooks/useGetProductDetails";
import { useGetProductReviews } from "../hooks/useGetProductReviews";
import { useGetSimilarProduct } from "../hooks/useGetSimilarProduct";
import { useImageIndex } from "../utils";
import ProductCard from "./ui/ProductCard";

const LABELS: Record<string, [string, string?]> = {
  pileHeightMm: ["Pile height", "mm"],
  washTempC: ["Wash temperature", "°C"],
  maxLoadKg: ["Max load", "kg"],
  maxWatt: ["Max power", "W"],
  cableLengthCm: ["Cable length", "cm"],
  burnTimeHours: ["Burn time", "hours"],
  warrantyYears: ["Warranty", "years"],
  weightKg: ["Weight", "kg"],
};

function attribute(key: string, value: string | number | boolean) {
  const [label, unit] = LABELS[key] ?? [
    key.replace(/([A-Z])/g, " $1").replace(/^./, (c) => c.toUpperCase()),
  ];
  const text =
    typeof value === "boolean"
      ? value
        ? "Yes"
        : "No"
      : `${value}${unit ? ` ${unit}` : ""}`;
  return { label, text };
}

function stockLabel(stock: number) {
  if (stock <= 0) return "Sold out";
  return stock <= 2 ? `Only ${stock} left` : "In stock";
}

const chip = (active: boolean, soldOut: boolean) =>
  `rounded-xl border px-4 py-1.5 text-sm font-semibold ${
    active ? "border-navy bg-navy text-white" : "border-dusk bg-white text-navy"
  } ${soldOut ? "line-through opacity-60" : ""}`;

function Reviews({ slug }: { slug: string }) {
  const [page, setPage] = useState(1);
  const { data, isPending, isError } = useGetProductReviews(slug, page);

  if (isPending) return <p>Loading reviews…</p>;
  if (isError) return <p>Could not load reviews.</p>;
  if (data.items.length === 0)
    return <p className="text-navy-700">No reviews yet.</p>;

  return (
    <div>
      <ul className="grid gap-4">
        {map(data.items, (r) => (
          <li
            key={r.id}
            className="rounded-xl border border-dusk-100 bg-white p-4"
          >
            <p className="font-bold">
              {"★".repeat(r.rating)}
              {"☆".repeat(5 - r.rating)} {r.title}
            </p>
            {r.body && <p className="mt-1">{r.body}</p>}
            <p className="mt-2 text-sm text-navy-700">
              {new Date(r.createdAt).toLocaleDateString()}
              {r.verifiedPurchase && " · Verified purchase"}
            </p>
          </li>
        ))}
      </ul>

      {data.totalPages > 1 && (
        <div className="mt-4 flex items-center gap-4">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            className="font-semibold disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm">
            Page {page} of {data.totalPages}
          </span>
          <button
            type="button"
            disabled={page >= data.totalPages}
            onClick={() => setPage(page + 1)}
            className="font-semibold disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default function ProductPage({ slug }: { slug: string }) {
  const router = useRouter();
  const { data: p, isPending, isError } = useGetProductDetails(slug);
  const { data: similar } = useGetSimilarProduct(slug);
  const [sku, setSku] = useState<string>();
  const { index: imgIndex, select: setImgIndex } = useImageIndex();

  if (isPending)
    return <p className="mx-auto max-w-7xl px-5 py-10">Loading…</p>;
  if (isError) {
    return (
      <div className="mx-auto w-full max-w-7xl px-5 py-10">
        <p className="text-navy/70">Product not found.</p>
        <Link
          href="/products"
          className="mt-4 inline-block font-semibold text-navy hover:underline"
        >
          Back to products
        </Link>
      </div>
    );
  }

  const v = p.variants.find((x) => x.sku === sku) ?? p.variants[0];
  const colors = [...new Set(map(p.variants, (x) => x.color))].filter(Boolean);
  const sizes = map(
    p.variants.filter((x) => x.color === v.color),
    (x) => x.size,
  ).filter(Boolean);
  const pick = (color: string | null, size: string | null) =>
    (
      p.variants.find((x) => x.color === color && x.size === size) ??
      p.variants.find((x) => x.color === color)
    )?.sku;

  const img = p.images[imgIndex];
  const attrs = Object.entries(p.attributes).filter(
    ([, val]) => val !== null && val !== "",
  );

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-8">
      <nav className="mb-6 flex items-center gap-2 text-sm text-navy-700">
        <button
          type="button"
          aria-label="Go back"
          onClick={() => router.back()}
          className="inline-flex items-center hover:text-navy"
        >
          <ArrowLeft size={16} aria-hidden="true" />
        </button>
        <Link href="/products" className="hover:underline">
          Shop
        </Link>
        {map(p.categoryPath, (c) => (
          <span key={c.slug}>
            {" › "}
            <Link
              href={`/products?category=${c.slug}`}
              className="hover:underline"
            >
              {c.name}
            </Link>
          </span>
        ))}
      </nav>

      <div className="grid gap-8 md:grid-cols-2">
        <div>
          <div className="relative aspect-square overflow-hidden rounded-2xl bg-dusk-100">
            <ProductImage
              src={img.url}
              alt={img.alt ?? p.name}
              sizes="(min-width: 768px) 50vw, 100vw"
              priority
            />
          </div>
          {p.images.length > 1 && (
            <div className="mt-3 flex gap-2">
              {map(p.images, (im, i) => (
                <button
                  type="button"
                  key={im.url}
                  onClick={() => setImgIndex(i)}
                  className={`relative size-16 overflow-hidden rounded-lg border-2 ${i === imgIndex ? "border-navy" : "border-transparent"}`}
                >
                  <ProductImage
                    src={im.url}
                    alt={im.alt ?? p.name}
                    sizes="64px"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <p className="text-navy-700">{p.brand.name}</p>
          <h1 className="text-4xl font-extrabold tracking-tight">{p.name}</h1>
          <p className="mt-1 text-sm text-navy-700">
            {p.ratingAverage !== null
              ? `★ ${p.ratingAverage.toFixed(1)} (${p.reviewCount} reviews)`
              : "No reviews yet"}
          </p>

          <p className="mt-4 flex items-baseline gap-3">
            <span className="text-3xl font-extrabold">
              {formatPrice(v.price)}
            </span>
            {v.compareAtPrice !== null && v.compareAtPrice > v.price && (
              <span className="text-navy-700 line-through">
                {formatPrice(v.compareAtPrice)}
              </span>
            )}
          </p>
          <p
            className={`mt-1 font-semibold ${v.stock <= 0 ? "text-red-700" : ""}`}
          >
            {stockLabel(v.stock)}
          </p>
          <p className="text-sm text-navy-700">SKU: {v.sku}</p>

          {colors.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {map(colors, (c) => (
                <button
                  type="button"
                  key={c}
                  onClick={() => setSku(pick(c, v.size))}
                  className={chip(c === v.color, false)}
                >
                  {c}
                </button>
              ))}
            </div>
          )}
          {sizes.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {map(sizes, (s) => {
                const target = p.variants.find(
                  (x) => x.color === v.color && x.size === s,
                );
                return (
                  <button
                    type="button"
                    key={s}
                    onClick={() => setSku(pick(v.color, s))}
                    className={chip(s === v.size, (target?.stock ?? 0) <= 0)}
                  >
                    {s}
                  </button>
                );
              })}
            </div>
          )}

          {p.description && <p className="mt-6">{p.description}</p>}

          {p.features.length > 0 && (
            <ul className="mt-4 list-disc pl-5">
              {map(p.features, (f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          )}

          {attrs.length > 0 && (
            <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-6 gap-y-1 text-sm">
              {map(attrs, ([key, val]) => {
                const a = attribute(key, val);
                return (
                  <div key={key} className="contents">
                    <dt className="text-navy-700">{a.label}</dt>
                    <dd>{a.text}</dd>
                  </div>
                );
              })}
            </dl>
          )}
        </div>
      </div>

      <section className="mt-12">
        <h2 className="mb-4 text-2xl font-extrabold tracking-tight">Reviews</h2>
        <Reviews slug={slug} />
      </section>

      {similar && similar.length > 0 && (
        <section className="mt-12">
          <h2 className="mb-4 text-2xl font-extrabold tracking-tight">
            Similar products
          </h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {map(similar, (s) => (
              <ProductCard key={s.id} product={s} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
