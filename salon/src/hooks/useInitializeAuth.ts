import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { apiClient } from "@/lib/utils";

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
 * Hook to initialize authentication on app load using React Query
 *
 * Uses /auth/me endpoint with cookie-based session.
 * Caches result so multiple consumers share the same request.
 */
export function useInitializeAuth() {
  const setUser = useAuthStore((state) => state.setUser);
  const setPermissions = useAuthStore((state) => state.setPermissions);
  const setTenant = useTenantStore((state) => state.setTenant);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const response = await apiClient.get<AuthMeResponse>("/auth/me");
      const userData = response.data.user;
      const permissions = response.data.permissions || [];

      if (userData && userData.id) {
        setUser({
          id: userData.id,
          email: userData.email,
          firstName: userData.firstName,
          lastName: userData.lastName,
          phone: userData.phone,
          role: userData.role,
          roleNames: userData.roleNames,
          tenantId: userData.tenantId,
        });
        setPermissions(permissions);
        setTenant({
          id: userData.tenantId,
          name: "",
          subdomain: "",
          subscriptionTier: "starter",
          status: "active",
          isPublished: false,
        });
      } else {
        setUser(null);
        setPermissions([]);
        setTenant(null);
      }

      return userData;
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
}
