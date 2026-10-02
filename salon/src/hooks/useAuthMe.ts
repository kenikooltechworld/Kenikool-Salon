import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth";
import { useInitializeAuth } from "./useInitializeAuth";
import type { User } from "@/stores/auth";

export function useAuthMe(): UseQueryResult<User | null, Error> {
  const authQuery = useInitializeAuth();

  const user: User | null = authQuery.data
    ? {
        id: authQuery.data.id,
        email: authQuery.data.email,
        firstName: authQuery.data.firstName,
        lastName: authQuery.data.lastName,
        phone: authQuery.data.phone,
        role: authQuery.data.role,
        roleNames: authQuery.data.roleNames,
        tenantId: authQuery.data.tenantId,
        avatar: authQuery.data.avatar,
      }
    : null;

  return {
    ...authQuery,
    data: user,
  } as UseQueryResult<User | null, Error>;
}
