import { House } from "lucide-react";
import { cacheLife } from "next/cache";
import Link from "next/link";
import {
  QUICK_LINKS,
  SHOP_LINKS,
  SITE_NAME,
  SITE_TAGLINE,
} from "@/shared/data/navigations";

const linkClass = "hover:text-navy hover:underline hover:underline-offset-4";

function LinkColumn({
  title,
  links,
}: {
  title: string;
  links: { href: string; label: string }[];
}) {
  return (
    <nav aria-label={title}>
      <h2 className="mb-3 text-base font-bold text-navy">{title}</h2>
      <ul className="grid gap-2">
        {links.map((l) => (
          <li key={l.href}>
            <Link href={l.href} className={linkClass}>
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default async function Footer() {
  "use cache";
  cacheLife("days");

  const year = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-dusk-100 bg-white text-navy/70">
      <div className="mx-auto grid w-full max-w-7xl gap-8 px-5 py-12 md:grid-cols-[2fr_1fr_1fr]">
        <div>
          <Link
            href="/"
            className="flex items-center gap-2 text-2xl font-extrabold tracking-tighter text-navy"
          >
            <House size={22} className="text-dusk" aria-hidden="true" />
            {SITE_NAME}
          </Link>
          <p className="mt-3 max-w-[32ch]">{SITE_TAGLINE}</p>
        </div>
        <LinkColumn title="Shop" links={SHOP_LINKS} />
        <LinkColumn title="Quick links" links={QUICK_LINKS} />
      </div>

      <div className="mx-auto flex w-full max-w-7xl flex-wrap justify-between gap-x-6 gap-y-2 border-t border-dusk-100 px-5 pb-8 pt-5 text-sm">
        <span>
          © {year} {SITE_NAME}. Prices in EUR.
        </span>
        <span>Demo shop built for a coding assignment.</span>
      </div>
    </footer>
  );
}
