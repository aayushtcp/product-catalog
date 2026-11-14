import { House, SearchX } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <section className="mx-auto flex w-full max-w-7xl flex-col items-center px-5 py-24 text-center">
      <SearchX size={56} className="text-dusk" aria-hidden="true" />
      <p className="mt-6 text-sm font-semibold uppercase tracking-widest text-navy/60">
        404
      </p>
      <h1 className="mt-2 text-4xl font-extrabold tracking-tight text-navy md:text-5xl">
        Page not found
      </h1>
      <p className="mt-4 max-w-[48ch] text-lg text-navy/70">
        We couldn&apos;t find the page you were looking for. It may have moved
        or no longer exists.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-xl bg-navy px-6 py-3 font-bold text-white transition-colors hover:bg-navy-800"
        >
          <House size={18} aria-hidden="true" />
          Back home
        </Link>
        <Link
          href="/products"
          className="inline-flex items-center gap-2 rounded-xl border border-dusk-100 bg-white px-6 py-3 font-bold text-navy transition-colors hover:border-navy"
        >
          Browse products
        </Link>
      </div>
    </section>
  );
}
