import { useQuery, type UseQueryResult } from "@tanstack/react-query";
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

export function useAuthUser(): UseQueryResult<AuthMeResponse["user"] | undefined, Error> {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const response = await apiClient.get<AuthMeResponse>("/auth/me");
      return response.data.user;
    },
    retry: false,
    staleTime: 0,
    gcTime: 5 * 60 * 1000,
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
}
