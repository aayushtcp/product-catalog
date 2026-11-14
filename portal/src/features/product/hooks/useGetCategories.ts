import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { CategoryNode } from "../types/product";

export const useGetCategories = () =>
  useQuery({
    queryKey: productKeys.categories(),
    queryFn: async () =>
      (await api.get<CategoryNode[]>(ENDPOINTS.categories)).data,
  });
