import { Suspense } from "react";
import CollectionsPage from "@/features/collection/components/CollectionsPage";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto w-full max-w-7xl px-5 py-10">
          <p className="text-navy/70">Loading collections…</p>
        </div>
      }
    >
      <CollectionsPage />
    </Suspense>
  );
}
