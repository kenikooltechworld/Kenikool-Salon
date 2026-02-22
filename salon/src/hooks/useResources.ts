import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Resource {
  id: string;
  name: string;
  type: "room" | "chair" | "equipment" | "tool" | "supply";
  description?: string;
  location_id?: string;
  quantity: number;
  available_quantity: number;
  status: "active" | "inactive" | "maintenance";
  is_active: boolean;
  purchase_date?: string;
  purchase_price?: number;
  depreciation_value?: number;
  maintenance_cost: number;
  tags: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ResourceAvailability {
  id: string;
  resource_id: string;
  day_of_week?: string;
  start_time: string;
  end_time: string;
  is_recurring: boolean;
  effective_from?: string;
  effective_to?: string;
  is_active: boolean;
}

export interface ResourceAssignment {
  id: string;
  appointment_id: string;
  resource_id: string;
  quantity_used: number;
  status: "assigned" | "in_use" | "released" | "cancelled";
  assigned_at: string;
  released_at?: string;
}

interface ResourceFilters {
  type?: string;
  status?: string;
  location_id?: string;
}

interface CreateResourceInput {
  name: string;
  type: "room" | "chair" | "equipment" | "tool" | "supply";
  description?: string;
  location_id?: string;
  quantity: number;
  purchase_date?: string;
  purchase_price?: number;
  tags?: string[];
  notes?: string;
}

interface UpdateResourceInput {
  name?: string;
  description?: string;
  quantity?: number;
  status?: "active" | "inactive" | "maintenance";
  tags?: string[];
  notes?: string;
}

// Fetch all resources
export const useResources = (filters?: ResourceFilters) => {
  return useQuery({
    queryKey: ["resources", filters],
    queryFn: async () => {
      const { data } = await apiClient.get("/resources", { params: filters });
      return data.data as Resource[];
    },
  });
};

// Fetch single resource
export const useResource = (resourceId: string) => {
  return useQuery({
    queryKey: ["resource", resourceId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/resources/${resourceId}`);
      return data.data as Resource;
    },
    enabled: !!resourceId,
  });
};

// Create resource
export const useCreateResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateResourceInput) => {
      const { data } = await apiClient.post("/resources", input);
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
};

// Update resource
export const useUpdateResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: UpdateResourceInput;
    }) => {
      const response = await apiClient.patch(`/resources/${id}`, data);
      return response.data.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      queryClient.invalidateQueries({ queryKey: ["resource", id] });
    },
  });
};

// Delete resource
export const useDeleteResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (resourceId: string) => {
      await apiClient.delete(`/resources/${resourceId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
};

// Reserve resource
export const useReserveResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      resourceId,
      quantity,
    }: {
      resourceId: string;
      quantity: number;
    }) => {
      const { data } = await apiClient.post(
        `/resources/${resourceId}/reserve`,
        { quantity },
      );
      return data.data;
    },
    onSuccess: (_, { resourceId }) => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      queryClient.invalidateQueries({ queryKey: ["resource", resourceId] });
    },
  });
};

// Release resource
export const useReleaseResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      resourceId,
      quantity,
    }: {
      resourceId: string;
      quantity: number;
    }) => {
      const { data } = await apiClient.post(
        `/resources/${resourceId}/release`,
        { quantity },
      );
      return data.data;
    },
    onSuccess: (_, { resourceId }) => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      queryClient.invalidateQueries({ queryKey: ["resource", resourceId] });
    },
  });
};

// Get resource availability
export const useResourceAvailability = (resourceId: string) => {
  return useQuery({
    queryKey: ["resource-availability", resourceId],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/resources/${resourceId}/availability`,
      );
      return data.data as ResourceAvailability[];
    },
    enabled: !!resourceId,
  });
};

// Update resource availability
export const useUpdateResourceAvailability = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      resourceId,
      availability,
    }: {
      resourceId: string;
      availability: Partial<ResourceAvailability>[];
    }) => {
      const { data } = await apiClient.patch(
        `/resources/${resourceId}/availability`,
        {
          availability,
        },
      );
      return data.data;
    },
    onSuccess: (_, { resourceId }) => {
      queryClient.invalidateQueries({
        queryKey: ["resource-availability", resourceId],
      });
    },
  });
};

// Mark resource as maintenance
export const useMarkResourceMaintenance = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (resourceId: string) => {
      const { data } = await apiClient.patch(
        `/resources/${resourceId}/maintenance`,
      );
      return data.data;
    },
    onSuccess: (_, resourceId) => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      queryClient.invalidateQueries({ queryKey: ["resource", resourceId] });
    },
  });
};

// Get resource assignments for appointment
export const useResourceAssignments = (appointmentId: string) => {
  return useQuery({
    queryKey: ["resource-assignments", appointmentId],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/resources/assignments/${appointmentId}`,
      );
      return data.data as ResourceAssignment[];
    },
    enabled: !!appointmentId,
  });
};

// Assign resource to appointment
export const useAssignResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      appointmentId,
      resourceId,
      quantity,
    }: {
      appointmentId: string;
      resourceId: string;
      quantity: number;
    }) => {
      const { data } = await apiClient.post("/resources/assign", {
        appointment_id: appointmentId,
        resource_id: resourceId,
        quantity_used: quantity,
      });
      return data.data;
    },
    onSuccess: (_, { appointmentId }) => {
      queryClient.invalidateQueries({
        queryKey: ["resource-assignments", appointmentId],
      });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
};

// Release resource assignment
export const useReleaseResourceAssignment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (assignmentId: string) => {
      const { data } = await apiClient.patch(
        `/resources/assignments/${assignmentId}/release`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resource-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
};
