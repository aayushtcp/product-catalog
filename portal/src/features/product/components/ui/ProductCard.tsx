import Link from "next/link";
import ProductImage from "@/shared/components/ui/ProductImage";
import { formatPrice } from "@/shared/utils";
import type { ProductCardData } from "../../types/product";

export default function ProductCard({
  product: p,
}: {
  product: ProductCardData;
}) {
  const hasRange =
    p.price !== null && p.priceMax !== null && p.priceMax > p.price;
  const onSale =
    p.price !== null && p.compareAtPrice !== null && p.compareAtPrice > p.price;

  return (
    <Link
      href={`/products/${p.slug}`}
      className="group block overflow-hidden rounded-2xl border border-dusk-100 bg-white"
    >
      <div className="relative aspect-square bg-dusk-100">
        <ProductImage
          src={p.image?.url}
          alt={p.image?.alt ?? p.name}
          sizes="(min-width: 768px) 25vw, 50vw"
        />
        {!p.inStock && (
          <span className="absolute left-3 top-3 rounded-full bg-navy px-3 py-1 text-xs font-bold text-white">
            Sold out
          </span>
        )}
      </div>

      <div className="p-4">
        <p className="text-sm text-navy-700">{p.brand.name}</p>
        <h3 className="font-bold leading-tight group-hover:underline">
          {p.name}
        </h3>

        <p className="mt-2 flex items-baseline gap-2">
          {p.price === null ? (
            <span className="text-navy-700">Price unavailable</span>
          ) : (
            <>
              <span className="font-extrabold">
                {hasRange && "from "}
                {formatPrice(p.price)}
              </span>
              {onSale && p.compareAtPrice !== null && (
                <span className="text-sm text-navy-700 line-through">
                  {formatPrice(p.compareAtPrice)}
                </span>
              )}
            </>
          )}
        </p>

        <p className="mt-1 text-sm text-navy-700">
          {p.ratingAverage !== null
            ? `★ ${p.ratingAverage.toFixed(1)} (${p.reviewCount})`
            : "No reviews yet"}
        </p>
      </div>
    </Link>
  );
}
