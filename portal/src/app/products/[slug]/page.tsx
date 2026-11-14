import { Suspense } from "react";
import ProductDetailPage from "@/features/product/components/ProductDetailPage";

export default function Page({ params }: PageProps<"/products/[slug]">) {
  return (
    <Suspense
      fallback={
        <div className="mx-auto w-full max-w-7xl px-5 py-10">
          <p className="text-navy/70">Loading product…</p>
        </div>
      }
    >
      <ProductDetail params={params} />
    </Suspense>
  );
}

async function ProductDetail({
  params,
}: {
  params: PageProps<"/products/[slug]">["params"];
}) {
  const { slug } = await params;
  return <ProductDetailPage slug={slug} />;
}
