import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { useEffect } from "react";
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

export function useInitializeAuth(): UseQueryResult<AuthMeResponse["user"] | undefined, Error> {
  const setUser = useAuthStore((state) => state.setUser);
  const setPermissions = useAuthStore((state) => state.setPermissions);
  const setTenant = useTenantStore((state) => state.setTenant);
  const setIsLoading = useAuthStore((state) => state.setIsLoading);

  const query = useQuery({
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
    staleTime: 0,
    gcTime: 5 * 60 * 1000,
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  useEffect(() => {
    if (!query.isLoading) {
      setIsLoading(false);
    }
  }, [query.isLoading, setIsLoading]);

  return query;
}
