import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { get } from "@/lib/utils/api";

interface AuthMeResponse {
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    role: string;
    roleNames: string[];
    tenantId: string;
    avatar?: string;
  };
  permissions: string[];
}

/**
 * Hook to initialize authentication on app load
 *
 * Fetches the current user from the cookie-based session via /auth/me endpoint.
 * This ensures users stay logged in after page refresh.
 *
 * Design rationale:
 * - Tokens are stored in httpOnly cookies (secure, not accessible to JS)
 * - On app load, we fetch the current user from the session cookie
 * - If user has a valid session, they stay logged in
 * - If session is invalid/expired, they're logged out
 * - Unauthenticated users see the landing page without errors
 */
export function useInitializeAuth() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const setUser = useAuthStore((state) => state.setUser);
  const setPermissions = useAuthStore((state) => state.setPermissions);
  const setTenant = useTenantStore((state) => state.setTenant);

  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      try {
        // Try to fetch current user from cookie-based session
        const response = await get<AuthMeResponse>("/auth/me");

        if (isMounted) {
          setUser(response.user);
          setPermissions(response.permissions);
          // Set tenant in store (minimal tenant object with just ID)
          // Tenant context comes from httpOnly cookie, no need for localStorage
          setTenant({
            id: response.user.tenantId,
            name: "",
            subdomain: "",
            subscriptionTier: "starter",
            status: "active",
            isPublished: false,
          });
        }
      } catch (error) {
        // User is not authenticated or session is invalid
        // This is expected for unauthenticated users
        if (isMounted) {
          setUser(null);
          setPermissions([]);
          setTenant(null);
        }
      } finally {
        if (isMounted) {
          setIsInitialized(true);
          setIsLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, [setUser, setPermissions, setTenant]);

  return { isInitialized, isLoading };
}
