"use client";

import map from "lodash/map";
import Button from "@/shared/components/ui/Button";
import { useGetCollections } from "../hooks/useGetCollections";
import CollectionCard from "./ui/CollectionCard";

const SKELETON_ITEMS = [1, 2, 3, 4, 5, 6];

export default function CollectionsPage() {
  const { data, isPending, isError, refetch } = useGetCollections();

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-10">
      <h1 className="text-3xl font-extrabold tracking-tight text-navy md:text-4xl">
        Collections
      </h1>

      {isPending && (
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {map(SKELETON_ITEMS, (item) => (
            <div
              key={item}
              className="h-48 animate-pulse rounded-2xl bg-dusk-100"
            />
          ))}
        </div>
      )}

      {isError && (
        <div className="mt-8 rounded-2xl border border-dusk-100 bg-white p-6">
          <p className="font-semibold text-navy">Could not load collections.</p>
          <Button
            variant="primary"
            onClick={() => refetch()}
            className="mt-3 rounded-xl px-4 py-2"
          >
            Try again
          </Button>
        </div>
      )}

      {!isPending && !isError && data && data.length === 0 && (
        <div className="mt-8 rounded-2xl border border-dusk-100 bg-white p-6">
          <p className="font-semibold text-navy">No collections available.</p>
          <p className="mt-1 text-navy/70">
            Check back soon for new collections.
          </p>
        </div>
      )}

      {!isPending && !isError && data && data.length > 0 && (
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {map(data, (collection) => (
            <CollectionCard key={collection.slug} collection={collection} />
          ))}
        </div>
      )}
    </div>
  );
}
