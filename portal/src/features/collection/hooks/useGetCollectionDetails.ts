import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { collectionKeys } from "../constants/queryKeys";
import type { CollectionDetail } from "../types/collection";
import { PAGE_SIZE } from "../utils";

export const useGetCollectionDetails = (slug: string, page = 1) =>
  useQuery({
    queryKey: collectionKeys.detail(slug, page),
    queryFn: async () =>
      (
        await api.get<CollectionDetail>(ENDPOINTS.detail(slug), {
          params: { page, limit: PAGE_SIZE },
        })
      ).data,
    placeholderData: keepPreviousData,
    retry: false,
  });
