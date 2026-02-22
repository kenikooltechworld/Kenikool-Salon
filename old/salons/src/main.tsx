import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AuthProvider } from "@/lib/hooks/useAuth";
import { ToastProvider } from "@/components/ui/toast";
import { initPerformanceMonitoring } from "@/lib/utils/performance-monitoring";
import { registerServiceWorker } from "@/lib/utils/service-worker-register";
import "animate.css";
import "./index.css";
import App from "./App.tsx";

// Initialize performance monitoring
initPerformanceMonitoring();

// Register service worker for offline support and caching
if (import.meta.env.MODE === "production") {
  registerServiceWorker().catch((error) => {
    console.error("Failed to register service worker:", error);
  });
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
      gcTime: 1000 * 60 * 60 * 24, // 24 hours
    },
  },
});

// Persist React Query cache to localStorage
if (typeof window !== "undefined") {
  // Restore cache on app load
  try {
    const savedCache = localStorage.getItem("REACT_QUERY_OFFLINE_CACHE");
    if (savedCache) {
      const cache = JSON.parse(savedCache);
      Object.entries(cache).forEach(([key, value]) => {
        try {
          const queryKey = JSON.parse(key);
          queryClient.setQueryData(queryKey, value);
        } catch (e) {
          // Skip invalid cache entries
        }
      });
    }
  } catch (error) {
    console.error("Failed to restore cache from localStorage:", error);
  }

  // Save cache to localStorage whenever queries change
  queryClient.getQueryCache().subscribe((event) => {
    if (event.type === "updated" && event.action.type === "success") {
      try {
        const state = queryClient.getQueryCache().getAll();
        const cacheData: Record<string, unknown> = {};
        state.forEach((query) => {
          if (query.state.status === "success") {
            cacheData[JSON.stringify(query.queryKey)] = query.state.data;
          }
        });
        localStorage.setItem(
          "REACT_QUERY_OFFLINE_CACHE",
          JSON.stringify(cacheData),
        );
      } catch (error) {
        console.error("Failed to save cache to localStorage:", error);
      }
    }
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider defaultTheme="default" defaultMode="light">
          <AuthProvider>
            <ToastProvider>
              <App />
            </ToastProvider>
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
