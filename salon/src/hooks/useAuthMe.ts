import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { apiClient } from "@/lib/utils/api";

/**
 * Hook to fetch current user data from /auth/me endpoint using react-query
 *
 * Use this in protected routes to verify authentication and load user data.
 * This is NOT called automatically on app load - only when needed.
 *
 * Returns react-query result with:
 * - isLoading: true while fetching user data
 * - error: error if fetch fails
 * - data: user data if authenticated
 */
export function useAuthMe() {
  const setUser = useAuthStore((state) => state.setUser);
  const setPermissions = useAuthStore((state) => state.setPermissions);
  const setTenant = useTenantStore((state) => state.setTenant);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const response = await apiClient.get("/auth/me");
      const userData = response.data?.data || response.data;

      if (userData && userData.id) {
        // Restore user to auth store
        setUser({
          id: userData.id,
          email: userData.email,
          firstName: userData.first_name,
          lastName: userData.last_name,
          phone: userData.phone,
          role: userData.role_ids?.[0] || "user",
          roleNames: userData.role_names || [],
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
            const tenantData = tenantResponse.data?.data || tenantResponse.data;

            if (tenantData) {
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

      return userData;
    },
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
