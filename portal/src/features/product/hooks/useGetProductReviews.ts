import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { ENDPOINTS } from "../constants/endpoints";
import { productKeys } from "../constants/queryKeys";
import type { Paged, Review } from "../types/product";
import { api } from "@/shared/api";

export const useGetProductReviews = (slug: string, page = 1, limit = 5) =>
  useQuery({
    queryKey: productKeys.reviews(slug, page),
    queryFn: async () =>
      (
        await api.get<Paged<Review>>(ENDPOINTS.reviews(slug), {
          params: { page, limit },
        })
      ).data,
    placeholderData: keepPreviousData,
  });
