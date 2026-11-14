import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { ProductDetail } from "../types/product";

export const useGetProductDetails = (slug: string) =>
  useQuery({
    queryKey: productKeys.detail(slug),
    queryFn: async () =>
      (await api.get<ProductDetail>(ENDPOINTS.detail(slug))).data,
    retry: false,
  });
