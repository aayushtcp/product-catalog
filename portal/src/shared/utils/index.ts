const eur = new Intl.NumberFormat("en-IE", {
  style: "currency",
  currency: "EUR",
});

export const formatPrice = (n: number) => eur.format(n);

export const PLACEHOLDER_IMAGE = "/images/placeholder.svg";

/**
 * Product images are served from `public/images`. The API returns absolute
 * URLs pointing at the backend, so keep only the `/images/...` path and let
 * Next.js serve the local copy.
 */
export function resolveImageUrl(url: string | null | undefined) {
  if (!url) return PLACEHOLDER_IMAGE;

  try {
    const { pathname } = new URL(url, "http://localhost");
    return pathname.startsWith("/images/") ? pathname : url;
  } catch {
    return url;
  }
}
