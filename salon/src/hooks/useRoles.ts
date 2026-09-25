import { useQuery, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";
import type { Role } from "@/types/role";

/**
 * Fetch all roles
 */
export function useRoles() {
  return useQuery({
    queryKey: ["roles"],
    queryFn: async () => {
      const response = await get<{ roles: Role[] }>("/roles");
      return response.roles || [];
    },
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}
