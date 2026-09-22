import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type {
  Notification,
  NotificationPreference,
} from "@/types/notification";

export type {
  Notification,
  NotificationPreference,
} from "@/types/notification";

interface NotificationFilters {
  type?: string;
  status?: "read" | "unread";
  limit?: number;
  offset?: number;
}

// Fetch notifications with filtering
export const useNotifications = (filters?: NotificationFilters) => {
  return useQuery({
    queryKey: ["notifications", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.append("notification_type", filters.type);
      if (filters?.status === "read") params.append("status", "read");
      if (filters?.status === "unread") params.append("status", "unread");
      if (filters?.limit) params.append("limit", filters.limit.toString());
      if (filters?.offset) params.append("skip", filters.offset.toString());

      const response = await apiClient.get(`/notifications?${params}`);
      const payload = response.data;
      return (Array.isArray(payload)
        ? payload
        : (payload?.notifications || payload?.data?.notifications || [])) as Notification[];
    },
    staleTime: 30000, // 30 seconds
  });
};

// Fetch single notification
export const useNotification = (notificationId: string) => {
  return useQuery({
    queryKey: ["notification", notificationId],
    queryFn: async () => {
      const response = await apiClient.get(`/notifications/${notificationId}`);
      return response.data as Notification;
    },
  });
};

// Mark notification as read
export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      const { data } = await apiClient.patch(
        `/notifications/${notificationId}/mark-read`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({
        queryKey: ["notifications-unread-count"],
      });
    },
  });
};

// Delete notification
export const useDeleteNotification = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      await apiClient.delete(`/notifications/${notificationId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

// Get unread count
export const useUnreadNotificationCount = () => {
  return useQuery({
    queryKey: ["notifications-unread-count"],
    queryFn: async () => {
      const response = await apiClient.get("/notifications/unread-count");
      const payload = response.data;
      return (payload?.data?.unread_count || payload?.unread_count || 0) as number;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Get notification preferences
export const useNotificationPreferences = () => {
  return useQuery({
    queryKey: ["notification-preferences"],
    queryFn: async () => {
      const response = await apiClient.get("/notifications/preferences");
      const payload = response.data;
      return (Array.isArray(payload) ? payload : []) as NotificationPreference[];
    },
  });
};

// Update notification preferences
export const useUpdateNotificationPreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (preferences: Partial<NotificationPreference>[]) => {
      const response = await apiClient.post("/notifications/preferences", {
        preferences,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
    },
  });
};

// Clear all notifications
export const useClearAllNotifications = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiClient.post("/notifications/clear-all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({
        queryKey: ["notifications-unread-count"],
      });
    },
  });
};
