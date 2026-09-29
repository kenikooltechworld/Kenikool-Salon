import { QueryClient } from "@tanstack/react-query";

const STALE_TIME = 10 * 60 * 1000;
const GC_TIME = 30 * 60 * 1000;

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: STALE_TIME,
        gcTime: GC_TIME,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
        refetchOnMount: false,
      },
      mutations: {
        retry: 1,
        retryDelay: 1000,
      },
    },
  });
}

export const queryClient = createQueryClient();
