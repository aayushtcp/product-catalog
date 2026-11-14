export const collectionKeys = {
  all: ["collections"] as const,
  list: () => ["collections", "list"] as const,
  detail: (slug: string, page: number) =>
    ["collections", "detail", slug, page] as const,
};
