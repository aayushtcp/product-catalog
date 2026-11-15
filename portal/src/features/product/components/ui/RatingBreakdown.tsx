import map from "lodash/map";
import type { RatingSummary } from "../../types/product";

function stars(rating: number) {
  const full = Math.round(rating);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

export default function RatingBreakdown({
  summary,
  isPending,
  isError,
}: {
  summary: RatingSummary | undefined;
  isPending: boolean;
  isError: boolean;
}) {
  if (isPending) {
    return <p className="text-navy-700">Loading rating breakdown…</p>;
  }

  if (isError || !summary) {
    return null;
  }

  if (summary.count === 0) {
    return null;
  }

  const average = summary.average ?? 0;

  return (
    <div className="grid gap-6 rounded-2xl border border-dusk-100 bg-dusk-50 p-5 md:grid-cols-[auto_1fr] md:gap-10">
      <div className="text-center md:text-left">
        <p className="text-5xl font-extrabold tracking-tight">
          {average.toFixed(1)}
        </p>
        <p className="mt-1 text-sunset" aria-hidden="true">
          {stars(average)}
        </p>
        <p className="text-sm text-navy-700">
          {summary.count} {summary.count === 1 ? "review" : "reviews"}
        </p>
      </div>

      <ul className="flex flex-col justify-center gap-2">
        {map(summary.breakdown, (bucket) => {
          const percent = Math.round((bucket.count / summary.count) * 100);
          return (
            <li key={bucket.rating} className="flex items-center gap-3 text-sm">
              <span className="w-10 shrink-0 tabular-nums">
                {bucket.rating} ★
              </span>
              <span
                className="h-2.5 flex-1 overflow-hidden rounded-full bg-dusk-100"
                aria-hidden="true"
              >
                <span
                  className="block h-full rounded-full bg-sunset"
                  style={{ width: `${percent}%` }}
                />
              </span>
              <span className="w-16 shrink-0 text-right tabular-nums text-navy-700">
                {bucket.count} ({percent}%)
              </span>
              <span className="sr-only">
                {bucket.rating} stars: {bucket.count} reviews ({percent}%)
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
