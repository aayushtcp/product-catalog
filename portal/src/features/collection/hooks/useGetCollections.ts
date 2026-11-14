import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api";
import { ENDPOINTS } from "../constants/endpoints";
import { collectionKeys } from "../constants/queryKeys";
import type { Collection } from "../types/collection";

export const useGetCollections = () =>
  useQuery({
    queryKey: collectionKeys.list(),
    queryFn: async () => (await api.get<Collection[]>(ENDPOINTS.list)).data,
  });
