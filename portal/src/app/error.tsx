"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";
import Button from "@/shared/components/ui/Button";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="mx-auto flex w-full max-w-7xl flex-col items-center px-5 py-24 text-center">
      <AlertTriangle size={56} className="text-dusk" aria-hidden="true" />
      <p className="mt-6 text-sm font-semibold uppercase tracking-widest text-navy/60">
        Something went wrong
      </p>
      <h1 className="mt-2 text-4xl font-extrabold tracking-tight text-navy md:text-5xl">
        We hit an unexpected error
      </h1>
      <p className="mt-4 max-w-[48ch] text-lg text-navy/70">
        Please try again. If the problem continues, come back later or return to
        the homepage.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button
          variant="primary"
          onClick={() => reset()}
          className="inline-flex items-center gap-2 rounded-full px-6 py-3"
        >
          <RefreshCw size={18} aria-hidden="true" />
          Try again
        </Button>
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-full border border-dusk-100 bg-white px-6 py-3 font-bold text-navy transition-colors hover:border-navy"
        >
          Back home
        </Link>
      </div>
    </section>
  );
}
