import { ArrowRight } from "lucide-react";
import Link from "next/link";
import type { Collection } from "../../types/collection";

export default function CollectionCard({
  collection: c,
}: {
  collection: Collection;
}) {
  return (
    <Link
      href={`/collections/${c.slug}`}
      className="group flex flex-col rounded-2xl border border-dusk-100 bg-white p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <h2 className="text-xl font-extrabold leading-tight">{c.name}</h2>
        <span className="shrink-0 rounded-xl bg-sunset-100 px-3 py-1 text-xs font-bold text-sunset-600">
          {c.productCount} {c.productCount === 1 ? "product" : "products"}
        </span>
      </div>

      <p className="mt-3 flex-1 text-navy/70">{c.description}</p>

      <span className="mt-5 inline-flex items-center gap-1 text-sm font-bold text-navy group-hover:underline">
        Browse collection
        <ArrowRight size={16} aria-hidden="true" />
      </span>
    </Link>
  );
}
