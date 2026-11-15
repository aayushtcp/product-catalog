import type { ProductListParams } from "../types/product";

export const productKeys = {
  all: ["products"] as const,
  list: (params: ProductListParams) => ["products", "list", params] as const,
  detail: (slug: string) => ["products", "detail", slug] as const,
  reviews: (slug: string, page: number) =>
    ["products", "reviews", slug, page] as const,
  reviewSummary: (slug: string) =>
    ["products", "reviews", "summary", slug] as const,
  similar: (slug: string) => ["products", "similar", slug] as const,
  categories: () => ["categories"] as const,
  brands: () => ["brands"] as const,
};
