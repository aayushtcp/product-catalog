import { Suspense } from "react";
import ProductsPage from "@/features/product/components/ProductsPage";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto w-full max-w-7xl px-5 py-10">
          <p className="text-navy/70">Loading products…</p>
        </div>
      }
    >
      <ProductsPage />
    </Suspense>
  );
}
