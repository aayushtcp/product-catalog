"use client";

import map from "lodash/map";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import ProductCard from "@/features/product/components/ui/ProductCard";
import Button from "@/shared/components/ui/Button";
import { useGetCollectionDetails } from "../hooks/useGetCollectionDetails";
import { getPageNavigation, getPaginationLabel, parsePage } from "../utils";

const SKELETON_ITEMS = [1, 2, 3, 4, 5, 6, 7, 8];

export default function CollectionDetails({ slug }: { slug: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const page = parsePage(searchParams.get("page"));
  const { data, isPending, isError } = useGetCollectionDetails(slug, page);

  function updatePage(next: number) {
    const nextParams = new URLSearchParams(searchParams.toString());
    if (next > 1) nextParams.set("page", String(next));
    else nextParams.delete("page");
    const query = nextParams.toString();
    router.push(query ? `${pathname}?${query}` : pathname);
  }

  if (isPending) {
    return (
      <div className="mx-auto w-full max-w-7xl px-5 py-10">
        <div className="h-4 w-40 animate-pulse rounded bg-dusk-100" />
        <div className="mt-6 h-10 w-72 max-w-full animate-pulse rounded bg-dusk-100" />
        <div className="mt-4 h-5 w-full max-w-xl animate-pulse rounded bg-dusk-100" />
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          {map(SKELETON_ITEMS, (item) => (
            <div
              key={item}
              className="aspect-3/4 animate-pulse rounded-2xl bg-dusk-100"
            />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto w-full max-w-7xl px-5 py-10">
        <p className="text-navy/70">Collection not found.</p>
        <Link
          href="/collections"
          className="mt-4 inline-block font-semibold text-navy hover:underline"
        >
          Back to collections
        </Link>
      </div>
    );
  }

  const { previous, next } = getPageNavigation(page, data.products.totalPages);

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-10">
      <nav className="mb-6 text-sm text-navy-700">
        <Link href="/collections" className="hover:underline">
          Collections
        </Link>
        <span> › </span>
        <span className="text-navy">{data.name}</span>
      </nav>

      <header className="max-w-3xl">
        <h1 className="text-3xl font-extrabold tracking-tight text-navy md:text-4xl">
          {data.name}
        </h1>
        <p className="mt-3 text-lg text-navy/70">{data.description}</p>
        <p className="mt-2 text-sm text-navy/60">
          {data.products.total}{" "}
          {data.products.total === 1 ? "product" : "products"}
        </p>
      </header>

      {data.products.items.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-dusk-100 bg-white p-6">
          <p className="font-semibold text-navy">
            No products in this collection yet.
          </p>
        </div>
      ) : (
        <>
          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {map(data.products.items, (product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          <div className="mt-8 flex items-center justify-between gap-4 border-t border-dusk-100 pt-6">
            <Button
              variant="ghost"
              disabled={previous === null}
              onClick={() => updatePage(previous ?? page)}
              className="rounded-xl border border-dusk-100 bg-white px-4 py-2 font-semibold disabled:opacity-40"
            >
              Previous
            </Button>
            <span className="text-sm text-navy/70">
              {getPaginationLabel(
                page,
                data.products.totalPages,
                data.products.total,
              )}
            </span>
            <Button
              variant="ghost"
              disabled={next === null}
              onClick={() => updatePage(next ?? page)}
              className="rounded-xl border border-dusk-100 bg-white px-4 py-2 font-semibold disabled:opacity-40"
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
