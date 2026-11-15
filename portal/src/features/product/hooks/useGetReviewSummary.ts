import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { RatingSummary } from "../types/product";

export const useGetReviewSummary = (slug: string) =>
  useQuery({
    queryKey: productKeys.reviewSummary(slug),
    queryFn: async () =>
      (await api.get<RatingSummary>(ENDPOINTS.reviewSummary(slug))).data,
  });
