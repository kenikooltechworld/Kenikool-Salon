import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { apiClient } from "@/lib/utils";
import type { User } from "@/stores/auth";

interface AuthMePayload {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role_ids: string[];
  role_names: string[];
  tenant_id: string;
  avatar?: string;
  permissions: string[];
}

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
export function useAuthMe(): UseQueryResult<User | null, Error> {
  const setUser = useAuthStore((state) => state.setUser);
  const setPermissions = useAuthStore((state) => state.setPermissions);
  const setTenant = useTenantStore((state) => state.setTenant);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const response = await apiClient.get<AuthMePayload>("/auth/me");
      const userData = response.data;

      if (userData && userData.id) {
        const user: User = {
          id: userData.id,
          email: userData.email,
          firstName: userData.first_name,
          lastName: userData.last_name,
          phone: userData.phone,
          role: userData.role_ids?.[0] || "user",
          roleNames: userData.role_names || [],
          tenantId: userData.tenant_id,
          avatar: userData.avatar,
        };
        setUser(user);
        setPermissions(userData.permissions || []);
        setTenant({
          id: userData.tenant_id,
          name: "",
          subdomain: "",
          subscriptionTier: "starter",
          status: "active",
          isPublished: false,
        });
        return user;
      }

      setUser(null);
      setPermissions([]);
      setTenant(null);
      return null;
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
}
