export type Ref = { slug: string; name: string };
export type Img = { url: string; alt: string | null };

export type Paged<T> = {
  items: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};

export type ProductSort =
  | "price_asc"
  | "price_desc"
  | "newest"
  | "rating"
  | "popular";

export type ProductListParams = {
  q?: string;
  category?: string;
  brand?: string; // comma-separated slugs
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
  minRating?: number;
  sort?: ProductSort;
  page?: number;
  limit?: number;
};

export type ProductCardData = {
  id: string;
  slug: string;
  name: string;
  brand: Ref;
  category: Ref;
  price: number | null;
  priceMax: number | null;
  compareAtPrice: number | null;
  inStock: boolean;
  ratingAverage: number | null;
  reviewCount: number;
  image: Img | null;
};

export type Variant = {
  sku: string;
  color: string | null;
  size: string | null;
  price: number;
  compareAtPrice: number | null;
  stock: number;
};

export type ProductDetail = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  brand: Ref;
  categoryPath: Ref[];
  attributes: Record<string, string | number | boolean>;
  features: string[];
  images: Img[];
  variants: Variant[];
  ratingAverage: number | null;
  reviewCount: number;
};

export type Review = {
  id: string;
  rating: number;
  title: string | null;
  body: string | null;
  verifiedPurchase: boolean;
  helpfulCount: number;
  createdAt: string;
};
