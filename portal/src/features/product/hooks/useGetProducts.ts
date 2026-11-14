import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type {
  Paged,
  ProductCardData,
  ProductListParams,
} from "../types/product";
import { api } from "@/shared/api";

export const useGetProducts = (params: ProductListParams) =>
  useQuery({
    queryKey: productKeys.list(params),
    queryFn: async () =>
      (await api.get<Paged<ProductCardData>>(ENDPOINTS.list, { params })).data,
    placeholderData: keepPreviousData,
  });
