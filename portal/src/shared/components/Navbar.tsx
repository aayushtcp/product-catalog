"use client";

import { House, Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import Button from "@/shared/components/ui/Button";
import { NAV_LINKS, SITE_NAME } from "@/shared/data/navigations";

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-dusk-100 bg-white/90 text-navy backdrop-blur-md">
      <div className="mx-auto flex min-h-16 w-full max-w-7xl items-center justify-between gap-4 px-5">
        <Link
          href="/"
          aria-label={`${SITE_NAME} home`}
          onClick={() => setOpen(false)}
          className="group flex items-center gap-2.5"
        >
          <span className="flex size-9 items-center justify-center rounded-xl bg-navy text-white transition-colors group-hover:bg-sunset">
            <House size={18} aria-hidden="true" />
          </span>
          <span className="text-xl font-extrabold tracking-tight md:text-2xl">
            {SITE_NAME}
          </span>
        </Link>

        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => {
            const active =
              pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-xl px-4 py-2 text-sm font-bold transition-colors ${
                  active
                    ? "bg-navy text-white"
                    : "text-navy/70 hover:bg-dusk-50 hover:text-navy"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <Button
          variant="ghost"
          aria-expanded={open}
          aria-controls="nav-panel"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((value) => !value)}
          className="flex size-10 items-center justify-center rounded-xl border border-dusk-100 md:hidden"
        >
          {open ? (
            <X size={22} aria-hidden="true" />
          ) : (
            <Menu size={22} aria-hidden="true" />
          )}
        </Button>
      </div>

      <nav
        id="nav-panel"
        aria-label="Main"
        className={`${open ? "block" : "hidden"} border-t border-dusk-100 md:hidden`}
      >
        <ul className="mx-auto flex w-full max-w-7xl flex-col gap-1 px-5 py-3">
          {NAV_LINKS.map((link) => {
            const active =
              pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setOpen(false)}
                  aria-current={active ? "page" : undefined}
                  className={`block rounded-xl px-4 py-3 font-semibold ${
                    active
                      ? "bg-navy text-white"
                      : "text-navy/70 hover:bg-dusk-50 hover:text-navy"
                  }`}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
