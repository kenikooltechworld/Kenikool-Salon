import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { apiClient } from "@/lib/utils/api";

/**
 * Hook to initialize authentication on app load
 * Restores user from /me endpoint if JWT token exists in httpOnly cookie
 * Also loads tenant data for the authenticated user
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
        // Try to fetch current user from /me endpoint
        // This will only succeed if JWT token exists in httpOnly cookie and is valid
        const response = await apiClient.get("/auth/me");

        // Handle wrapped response format { data: { ... } }
        const userData = response.data?.data || response.data;

        if (userData && userData.id && isMounted) {
          // Restore user to auth store
          setUser({
            id: userData.id,
            email: userData.email,
            firstName: userData.first_name,
            lastName: userData.last_name,
            phone: userData.phone,
            role: userData.role_ids?.[0] || "user",
            tenantId: userData.tenant_id,
          });

          // Set permissions if available
          if (userData.permissions) {
            setPermissions(userData.permissions);
          }

          // Load tenant data if tenant_id is available
          if (userData.tenant_id) {
            try {
              const tenantResponse = await apiClient.get(
                `/tenants/${userData.tenant_id}`,
              );
              const tenantData =
                tenantResponse.data?.data || tenantResponse.data;

              if (tenantData && isMounted) {
                setTenant({
                  id: tenantData.id,
                  name: tenantData.name,
                  subdomain: tenantData.subdomain,
                  subscriptionTier: tenantData.subscription_tier,
                  status: tenantData.status,
                  isPublished: tenantData.is_published,
                });
              }
            } catch (tenantError) {
              // Log but don't fail auth if tenant fetch fails
              console.error("Failed to load tenant data:", tenantError);
            }
          }
        }
      } catch (error) {
        // No valid JWT token or user not found - user is not authenticated
        // Backend will have cleared expired cookies, so frontend state is clean
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
