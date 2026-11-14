import Link from "next/link";
import { SITE_NAME, SITE_TAGLINE } from "@/shared/data/navigations";

export default function HomePage() {
  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-24">
      <h1 className="text-4xl font-extrabold tracking-tight text-navy md:text-5xl">
        {SITE_NAME}
      </h1>
      <p className="mt-4 max-w-[56ch] text-lg text-navy/70">{SITE_TAGLINE}</p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/products"
          className="rounded-full bg-sunset px-5 py-2.5 font-bold text-white transition-colors hover:bg-sunset-600"
        >
          Browse products
        </Link>
        <Link
          href="/collections"
          className="rounded-full border border-dusk-100 bg-white px-5 py-2.5 font-bold text-navy transition-colors hover:border-navy"
        >
          Collections
        </Link>
      </div>
    </section>
  );
}
