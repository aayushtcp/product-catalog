import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { ProductCardData } from "../types/product";

export const useGetSimilarProduct = (slug: string) =>
  useQuery({
    queryKey: productKeys.similar(slug),
    queryFn: async () =>
      (await api.get<ProductCardData[]>(ENDPOINTS.similar(slug))).data,
  });
