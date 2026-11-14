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

  const imagesPath = url.match(/(?:^|\/)(images\/[^\s?#]+)/);
  if (imagesPath) return `/${imagesPath[1]}`;

  const trimmed = url.trim();

  try {
    const { pathname } = new URL(trimmed, "http://localhost");
    return pathname.startsWith("/images/") ? pathname : trimmed;
  } catch {
    return PLACEHOLDER_IMAGE;
  }
}
