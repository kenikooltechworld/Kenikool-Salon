import { QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState, useEffect } from "react";
import {
  createOfflineQueryClient,
  persistQueryCache,
  restoreQueryCache,
} from "@/lib/offline/offline-query-client";

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(() => createOfflineQueryClient());
  const [isRestored, setIsRestored] = useState(false);

  useEffect(() => {
    // Restore cache on mount with timeout
    const restore = async () => {
      try {
        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Restore timeout")), 3000)
        );
        await Promise.race([restoreQueryCache(queryClient), timeoutPromise]);
      } catch (error) {
        console.warn("Failed to restore query cache:", error);
      } finally {
        setIsRestored(true);
      }
    };

    restore();

    // Persist cache periodically only when online
    const interval = setInterval(() => {
      if (navigator.onLine) {
        persistQueryCache(queryClient).catch(() => {});
      }
    }, 30000);

    return () => {
      clearInterval(interval);
      if (navigator.onLine) {
        persistQueryCache(queryClient).catch(() => {});
      }
    };
  }, [queryClient]);

  // Always render children, don't block on restore
  if (!isRestored) {
    return (
      <QueryClientProvider client={queryClient}>
        <div style={{ display: "none" }}>{children}</div>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
