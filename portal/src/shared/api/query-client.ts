import { environmentManager, QueryClient } from "@tanstack/react-query";
import { ApiError } from "./errors";

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) => {
          // Don't retry client errors (400, 404). Retrying won't change the answer.
          if (
            error instanceof ApiError &&
            error.status >= 400 &&
            error.status < 500
          ) {
            return false;
          }
          return failureCount < 2;
        },
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

export function getQueryClient() {
  // Server: always a new client, so data is never shared between requests.
  if (environmentManager.isServer()) return makeQueryClient();
  // Browser: reuse one client so the cache survives re-renders.
  browserQueryClient ??= makeQueryClient();
  return browserQueryClient;
}
