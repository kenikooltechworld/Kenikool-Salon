import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

interface MyTimeOffFilters {
  status?: string;
}

interface CreateMyTimeOffData {
  start_date: string;
  end_date: string;
  reason: string;
}

/**
 * Fetch current staff member's time off requests with filtering and sorting
 * Automatically filters by staff_id from authenticated user
 */
export function useMyTimeOffRequests(filters?: MyTimeOffFilters) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-time-off-requests", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<any>("/time-off-requests", {
        params: {
          staff_id: user?.id,
          ...filters,
        },
      });
      return data?.requests || [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch single time off request by ID (staff view)
 */
export function useMyTimeOffRequest(id: string) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-time-off-requests", id],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(`/time-off-requests/${id}`);
      return data || null;
    },
    enabled: !!id && !!user?.id,
  });
}

/**
 * Create new time off request for current staff member
 */
export function useCreateMyTimeOffRequest() {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);

  return useMutation({
    mutationFn: async (requestData: CreateMyTimeOffData) => {
      const { data } = await apiClient.post<any>("/time-off-requests", {
        staff_id: user?.id,
        ...requestData,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-time-off-requests"] });
    },
  });
}
