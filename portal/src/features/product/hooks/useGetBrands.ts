import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { Brand } from "../types/product";

export const useGetBrands = () =>
  useQuery({
    queryKey: productKeys.brands(),
    queryFn: async () => (await api.get<Brand[]>(ENDPOINTS.brands)).data,
  });
