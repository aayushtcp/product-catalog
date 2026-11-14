export const ENDPOINTS = {
  list: "/products/",
  detail: (slug: string) => `/products/${slug}/`,
  similar: (slug: string) => `/products/${slug}/similar/`,
  categories: "/categories/",
  brands: "/brands/",
  // Reviews live outside the /api prefix on the backend.
  reviews: (slug: string) => `/products/${slug}/reviews/`,
};
