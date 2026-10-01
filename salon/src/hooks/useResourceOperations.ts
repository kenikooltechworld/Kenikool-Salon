import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { Resource, ResourceAvailability, ResourceAssignment } from "@/hooks/useResources";

export interface AvailabilityInput {
  resource_id: string;
  day_of_week?: string;
  start_time: string;
  end_time: string;
  is_recurring: boolean;
  effective_from?: string;
  effective_to?: string;
  is_active: boolean;
}

export interface ResourceMaintenanceRecord {
  id: string;
  resource_id: string;
  maintenance_type: string;
  scheduled_date: string;
  completed_date?: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  description?: string;
  cost?: number;
  created_at: string;
}

const RESOURCES_QUERY_KEY = "resources";

// Resource Availability
export function useResourceAvailability(resourceId?: string) {
  return useQuery({
    queryKey: ["resource-availability", resourceId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/resources/${resourceId}/availability`);
      return data.data as ResourceAvailability[];
    },
    enabled: !!resourceId,
  });
}

export function useCreateResourceAvailability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: AvailabilityInput) => {
      const { data } = await apiClient.post("/resources/availability", input);
      return data.data;
    },
    onSuccess: (_, { resource_id }) => {
      queryClient.invalidateQueries({ queryKey: ["resource-availability", resource_id] });
    },
  });
}

export function useUpdateResourceAvailability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      resourceId,
      availability,
    }: {
      resourceId: string;
      availability: Partial<ResourceAvailability>[];
    }) => {
      const { data } = await apiClient.patch(`/resources/${resourceId}/availability`, {
        availability,
      });
      return data.data;
    },
    onSuccess: (_, { resourceId }) => {
      queryClient.invalidateQueries({ queryKey: ["resource-availability", resourceId] });
    },
  });
}

export function useDeleteResourceAvailability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (availabilityId: string) => {
      const { data } = await apiClient.delete(`/resources/availability/${availabilityId}`);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-availability"] });
    },
  });
}

// Resource Assignments
export function useResourceAssignments(appointmentId?: string) {
  return useQuery({
    queryKey: ["resource-assignments", appointmentId],
    queryFn: async () => {
      const { data } = await apiClient.get("/resources/assignments", {
        params: appointmentId ? { appointment_id: appointmentId } : undefined,
      });
      return data.data as ResourceAssignment[];
    },
    enabled: !!appointmentId,
  });
}

export function useAssignResource() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      appointment_id: string;
      resource_id: string;
      quantity_used: number;
    }) => {
      const { data } = await apiClient.post("/resources/assignments", input);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

export function useReleaseResourceAssignment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (assignmentId: string) => {
      const { data } = await apiClient.post(`/resources/assignments/${assignmentId}/release`);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

// Resource Maintenance
export function useResourceMaintenance(resourceId?: string) {
  return useQuery({
    queryKey: ["resource-maintenance", resourceId],
    queryFn: async () => {
      const { data } = await apiClient.get("/resources/maintenance", {
        params: resourceId ? { resource_id: resourceId } : undefined,
      });
      return data.data as ResourceMaintenanceRecord[];
    },
  });
}

export function useScheduleMaintenance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      resource_id: string;
      maintenance_type: string;
      scheduled_date: string;
      estimated_duration_hours?: number;
      description?: string;
      cost?: number;
    }) => {
      const { data } = await apiClient.post("/resources/maintenance", input);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

export function useCompleteMaintenance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (maintenanceId: string) => {
      const { data } = await apiClient.patch(`/resources/maintenance/${maintenanceId}/complete`);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

// Resource Utilization
export interface ResourceUtilizationStats {
  total_records: number;
  average_utilization: number;
  peak_utilization: number;
  min_utilization: number;
}

export function useResourceUtilizationStats(resourceId?: string) {
  return useQuery({
    queryKey: ["resource-utilization", resourceId],
    queryFn: async () => {
      const { data } = await apiClient.get("/resources/utilization/stats", {
        params: resourceId ? { resource_id: resourceId } : undefined,
      });
      return data as ResourceUtilizationStats;
    },
  });
}
