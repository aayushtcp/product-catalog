import { Suspense } from "react";
import CollectionDetails from "@/features/collection/components/CollectionDetails";

export default function Page({ params }: PageProps<"/collections/[slug]">) {
  return (
    <Suspense
      fallback={
        <div className="mx-auto w-full max-w-7xl px-5 py-10">
          <p className="text-navy/70">Loading collection…</p>
        </div>
      }
    >
      <CollectionDetail params={params} />
    </Suspense>
  );
}

async function CollectionDetail({
  params,
}: {
  params: PageProps<"/collections/[slug]">["params"];
}) {
  const { slug } = await params;
  return <CollectionDetails slug={slug} />;
}
