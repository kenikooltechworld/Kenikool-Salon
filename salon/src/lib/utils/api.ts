import axios from "axios";
import type {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

// Store for navigation callback (set by App component)
let navigationCallback: ((path: string) => void) | null = null;
let isInitializationComplete = false;

/**
 * Set the navigation callback for handling redirects
 * Called by App component after initialization
 */
export function setNavigationCallback(callback: (path: string) => void) {
  navigationCallback = callback;
  isInitializationComplete = true;
}

/**
 * Check if initialization is complete
 */
export function isInitComplete(): boolean {
  return isInitializationComplete;
}

// Retry configuration for resilient network handling
const MAX_RETRIES = 3;
const BASE_DELAY_MS = 500; // Start with 500ms
const MAX_DELAY_MS = 5000; // Cap at 5 seconds

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if HTTP method is idempotent (safe to retry)
 */
function isIdempotent(method?: string): boolean {
  return ["get", "head", "options", "put", "delete"].includes(
    (method || "").toLowerCase(),
  );
}

/**
 * Check if request has idempotency key (makes POST safe to retry)
 */
function hasIdempotencyKey(headers?: any): boolean {
  const key =
    headers?.["Idempotency-Key"] ||
    headers?.["idempotency-key"] ||
    headers?.["X-Idempotency-Key"];
  return Boolean(key);
}

/**
 * Determine if error is transient and request should be retried
 */
function shouldRetry(error: AxiosError): boolean {
  if (!error.config) return false;

  const status = error.response?.status;
  const code = (error as any).code;

  // Transient errors that are safe to retry
  const isTransient =
    !status || // Network errors
    code === "ECONNABORTED" || // Timeout
    code === "ETIMEDOUT" || // Connection timeout
    code === "ECONNRESET" || // Connection reset
    code === "ERR_NETWORK" || // Network error
    [408, 425, 429, 500, 502, 503, 504].includes(status); // Transient HTTP errors

  // Only retry if method is safe
  const safeMethod = isIdempotent(error.config.method);
  const postIsSafe =
    (error.config.method || "").toLowerCase() === "post" &&
    hasIdempotencyKey(error.config.headers);

  return isTransient && (safeMethod || postIsSafe);
}

/**
 * Calculate retry delay with exponential backoff and jitter
 */
function getRetryDelay(retryCount: number): number {
  // Exponential backoff: 500ms, 1000ms, 2000ms
  const exponentialDelay = BASE_DELAY_MS * Math.pow(2, retryCount - 1);

  // Add jitter (random 0-200ms) to prevent thundering herd
  const jitter = Math.random() * 200;

  // Cap at MAX_DELAY_MS
  return Math.min(exponentialDelay + jitter, MAX_DELAY_MS);
}

/**
 * Create and configure Axios instance for API requests with httpOnly cookies
 *
 * Features:
 * - No default timeout (relies on browser network timeouts)
 * - Automatic retry with exponential backoff for transient errors
 * - Request cancellation support via AbortController
 * - Idempotency key support for safe POST retries
 * - Request ID tracking for observability
 * - Token refresh on 401 errors
 *
 * Philosophy:
 * - Let requests complete naturally on slow networks
 * - Browser handles actual network failures
 * - Retry logic handles transient errors
 * - Per-request timeouts available when needed
 */
export function createApiClient(): AxiosInstance {
  const isPages =
    typeof window !== "undefined" &&
    window.location.hostname.endsWith(".pages.dev");
  const configuredBaseURL = (import.meta.env.VITE_API_URL || "").trim();
  const baseURL = isPages ? "/api/v1" : configuredBaseURL || "/api/v1";

  const client = axios.create({
    baseURL,
    // Set a reasonable default timeout to prevent infinite hangs in development
    // This helps catch backend connectivity issues early
    // Production apps can increase this or remove it based on requirements
    timeout: 30000, // 30 seconds
    withCredentials: true, // Enable sending cookies with requests
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Request interceptor - add request ID and timing metadata
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Add request ID for tracing
      if (!config.headers["X-Request-Id"]) {
        config.headers["X-Request-Id"] = crypto.randomUUID();
      }

      // Add timing metadata for latency tracking
      (config as any).metadata = { startTime: Date.now() };

      // Tenant context comes from httpOnly cookie (JWT token)
      // Backend extracts tenant_id from the access_token cookie
      // No need to send X-Tenant-ID header
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    },
  );

  // Response interceptor - handle retries, errors, and token refresh
  client.interceptors.response.use(
    (response) => {
      // Add client-side latency header for observability
      const metadata = (response.config as any).metadata;
      if (metadata?.startTime) {
        const latency = Date.now() - metadata.startTime;
        response.headers["x-client-latency-ms"] = String(latency);
      }
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
        _retryCount?: number;
      };

      // Initialize retry count
      if (!originalRequest._retryCount) {
        originalRequest._retryCount = 0;
      }

      // Don't retry refresh endpoint itself to prevent infinite loops
      const isRefreshEndpoint = originalRequest.url?.includes("/auth/refresh");

      // Retry logic for transient errors
      if (
        shouldRetry(error) &&
        !originalRequest._retry &&
        originalRequest._retryCount < MAX_RETRIES
      ) {
        originalRequest._retryCount += 1;

        // Calculate delay with exponential backoff and jitter
        const delay = getRetryDelay(originalRequest._retryCount);

        console.log(
          `Retrying request (attempt ${originalRequest._retryCount}/${MAX_RETRIES}) after ${delay}ms:`,
          originalRequest.url,
        );

        // Wait before retrying
        await sleep(delay);

        // Retry the request
        return client.request(originalRequest);
      }

      // Handle 401 Unauthorized - try to refresh token (but not for refresh endpoint)
      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !isRefreshEndpoint
      ) {
        originalRequest._retry = true;

        try {
          await client.post("/auth/refresh");

          return client(originalRequest);
        } catch (refreshError) {
          if (navigationCallback && isInitializationComplete) {
            const currentPath = window.location.pathname;
            const isPublicPage =
              currentPath === "/" || currentPath.startsWith("/public/");

            if (!isPublicPage) {
              navigationCallback("/auth/login");
            }
          }

          return Promise.reject(refreshError);
        }
      }

      // Handle 401 without retry (already tried refresh or is refresh endpoint)
      // Don't redirect on public pages
      if (error.response?.status === 401) {
        if (navigationCallback && isInitializationComplete) {
          const currentPath = window.location.pathname;
          const isPublicPage =
            currentPath === "/" || currentPath.startsWith("/public/");

          if (!isPublicPage) {
            navigationCallback("/auth/login");
          }
        }
      }

      // Handle 403 Forbidden - MFA required
      if (error.response?.status === 403) {
        const mfaRequired = error.response.headers["x-mfa-required"];
        if (
          mfaRequired === "true" &&
          navigationCallback &&
          isInitializationComplete
        ) {
          navigationCallback("/auth/mfa-verify");
        }
      }

      // Handle network errors with user-friendly messages
      if ((error as any).code === "ERR_NETWORK") {
        console.error("Network error:", originalRequest.url);
        error.message = "Network error. Please check your internet connection.";
      } else if (
        (error as any).code === "ECONNABORTED" ||
        (error as any).code === "ETIMEDOUT"
      ) {
        // Browser-level timeout or connection abort
        console.error("Connection timeout:", originalRequest.url);
        error.message =
          "Connection timeout. Please check your connection and try again.";
      }

      // Handle 500 Server Error - transform to user-friendly message
      if (error.response?.status === 500) {
        console.error("Server error", error.response?.data);

        // Extract user-friendly message from backend response
        const responseData = error.response?.data as any;
        const userMessage =
          responseData?.detail ||
          responseData?.message ||
          "A server error occurred. Please try again later.";

        // Attach user-friendly message to the error for UI consumption
        error.message = userMessage;
      }

      return Promise.reject(error);
    },
  );

  return client;
}

// Create default API client instance
export const apiClient = createApiClient();

// Export as 'api' for backward compatibility
export const api = apiClient;

/**
 * Optional timeout presets for specific operations that need time limits
 *
 * Note: No default timeout is set on the API client to allow requests to complete
 * naturally on slow networks. Use these presets only when you need explicit time limits.
 *
 * Common use cases:
 * - File uploads that should fail fast if stalled
 * - Operations with strict SLA requirements
 * - Background tasks that shouldn't block indefinitely
 */
export const TIMEOUTS = {
  FAST: 10000, // 10s - Quick operations that should fail fast
  STANDARD: 30000, // 30s - Standard operations with time limits
  SLOW: 60000, // 60s - Complex operations (reports, analytics)
  UPLOAD: 120000, // 2min - File uploads
} as const;

/**
 * Make GET request with optional timeout override
 */
export async function get<T>(
  url: string,
  config?: any & { timeout?: number },
): Promise<T> {
  const response = await apiClient.get<T>(url, config);
  return response.data;
}

/**
 * Make POST request with optional timeout override
 * Automatically adds idempotency key for safe retries
 */
export async function post<T>(
  url: string,
  data?: any,
  config?: any & { timeout?: number; idempotencyKey?: string },
): Promise<T> {
  const headers = { ...config?.headers };

  // Add idempotency key if not present (makes POST safe to retry)
  if (!headers["Idempotency-Key"] && config?.idempotencyKey) {
    headers["Idempotency-Key"] = config.idempotencyKey;
  }

  // Log the actual data being sent for staff creation
  if (url.includes("/staff")) {
    console.log("=== API POST REQUEST ===");
    console.log("URL:", url);
    console.log("Data being sent:", JSON.stringify(data, null, 2));
    console.log("Specialties in request:", data?.specialties);
    console.log("Certifications in request:", data?.certifications);
  }

  const response = await apiClient.post<T>(url, data, {
    ...config,
    headers,
  });

  // Log response for staff creation
  if (url.includes("/staff")) {
    console.log("=== API POST RESPONSE ===");
    console.log("Response data:", response.data);
  }

  return response.data;
}

/**
 * Make PUT request with optional timeout override
 */
export async function put<T>(
  url: string,
  data?: any,
  config?: any & { timeout?: number },
): Promise<T> {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
}

/**
 * Make PATCH request with optional timeout override
 */
export async function patch<T>(
  url: string,
  data?: any,
  config?: any & { timeout?: number },
): Promise<T> {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
}

/**
 * Make DELETE request with optional timeout override
 */
export async function del<T>(
  url: string,
  config?: any & { timeout?: number },
): Promise<T> {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
}

/**
 * Handle API errors
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.response?.data?.error) {
      return error.response.data.error;
    }
    if (error.message) {
      return error.message;
    }
  }
  return "An error occurred";
}
