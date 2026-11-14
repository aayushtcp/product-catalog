import type { ProductCardData } from "@/features/product/types/product";
import type { Page } from "@/shared/types/api";

export type Collection = {
  slug: string;
  name: string;
  description: string;
  productCount: number;
};

export type CollectionDetail = {
  slug: string;
  name: string;
  description: string;
  products: Page<ProductCardData>;
};
