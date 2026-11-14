"use client";

import { House, Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { type SubmitEvent, useEffect, useState } from "react";
import Button from "@/shared/components/ui/Button";
import { NAV_LINKS, SITE_NAME } from "@/shared/data/navigations";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    setOpen(false);
  }, []);

  function onSearch(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    const q = query.trim().replace(/\s+/g, " ");
    router.push(q ? `/products?q=${encodeURIComponent(q)}` : "/products");
    setOpen(false);
  }

  return (
    <header className="sticky top-0 z-50 border-b border-dusk-100 bg-white/95 text-navy backdrop-blur">
      <div className="mx-auto flex min-h-16 w-full max-w-7xl flex-wrap items-center gap-x-8 px-5 md:flex-nowrap">
        <Link
          href="/"
          aria-label={`${SITE_NAME} home`}
          className="mr-auto flex items-center gap-2 text-2xl font-extrabold tracking-tighter md:mr-0"
        >
          <House size={22} className="text-dusk" aria-hidden="true" />
          {SITE_NAME}
        </Link>

        <Button
          variant="primary"
          aria-expanded={open}
          aria-controls="nav-panel"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
          className="flex size-11 items-center justify-center rounded-lg md:hidden"
        >
          {open ? (
            <X size={24} aria-hidden="true" />
          ) : (
            <Menu size={24} aria-hidden="true" />
          )}
        </Button>

        <nav
          id="nav-panel"
          aria-label="Main"
          className={`${open ? "flex" : "hidden"} basis-full flex-col gap-4 border-t border-dusk-100 pb-5 pt-2 md:flex md:flex-1 md:basis-auto md:flex-row md:items-center md:justify-between md:border-0 md:p-0`}
        >
          <ul className="flex flex-col md:flex-row md:gap-6">
            {NAV_LINKS.map((link) => {
              const active =
                pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    aria-current={active ? "page" : undefined}
                    className={`block border-b-2 py-2 font-semibold md:py-1 ${
                      active
                        ? "border-navy text-navy"
                        : "border-transparent text-navy/70 hover:text-navy"
                    }`}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>

          <search className="md:w-80">
            <form onSubmit={onSearch} className="flex gap-2">
              <label htmlFor="nav-q" className="sr-only">
                Search products
              </label>
              <input
                id="nav-q"
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search products"
                className="w-full rounded-full border border-dusk-100 bg-dusk-50 px-4 py-2 text-navy placeholder:text-navy/50 focus:border-dusk focus:outline-none focus:ring-2 focus:ring-dusk/30"
              />
              <Button
                type="submit"
                variant="primary"
                className="rounded-full px-4 py-2"
              >
                Search
              </Button>
            </form>
          </search>
        </nav>
      </div>
    </header>
  );
}
