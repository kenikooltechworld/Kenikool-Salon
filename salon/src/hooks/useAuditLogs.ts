import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useState } from "react";

export interface AuditLog {
  id: string;
  event_type: string;
  resource: string;
  user_id?: string;
  ip_address: string;
  status_code: number;
  request_body?: Record<string, any>;
  response_body?: Record<string, any>;
  user_agent?: string;
  error_message?: string;
  duration_ms?: number;
  tags: string[];
  created_at: string;
}

export interface AuditSummary {
  period_days: number;
  total_events: number;
  unique_users: number;
  unique_ips: number;
  event_types: Record<string, number>;
  failed_attempts: number;
  start_date: string;
  end_date: string;
}

export const useAuditLogs = () => {
  const queryClient = useQueryClient();
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(100);
  const [eventType, setEventType] = useState<string | undefined>();
  const [resource, setResource] = useState<string | undefined>();
  const [userId, setUserId] = useState<string | undefined>();

  // List audit logs
  const {
    data: logsData,
    isLoading: isLoadingLogs,
    error: logsError,
  } = useQuery({
    queryKey: ["audit-logs", skip, limit, eventType, resource, userId],
    queryFn: async () => {
      const response = await apiClient.get("/audit/logs", {
        params: {
          skip,
          limit,
          event_type: eventType,
          resource,
          user_id: userId,
        },
      });
      return response.data;
    },
  });

  // Get user activity
  const { data: userActivityData, isLoading: isLoadingUserActivity } = useQuery(
    {
      queryKey: ["audit-logs", "user-activity", userId],
      queryFn: async () => {
        if (!userId) return null;
        const response = await apiClient.get(`/audit/user-activity/${userId}`);
        return response.data;
      },
      enabled: !!userId,
    },
  );

  // Get sensitive access logs
  const { data: sensitiveAccessData, isLoading: isLoadingSensitiveAccess } =
    useQuery({
      queryKey: ["audit-logs", "sensitive-access"],
      queryFn: async () => {
        const response = await apiClient.get("/audit/sensitive-access");
        return response.data;
      },
    });

  // Get failed access attempts
  const { data: failedAttemptsData, isLoading: isLoadingFailedAttempts } =
    useQuery({
      queryKey: ["audit-logs", "failed-attempts"],
      queryFn: async () => {
        const response = await apiClient.get("/audit/failed-attempts");
        return response.data;
      },
    });

  // Get audit summary
  const { data: auditSummary, isLoading: isLoadingSummary } = useQuery({
    queryKey: ["audit-logs", "summary"],
    queryFn: async () => {
      const response = await apiClient.get("/audit/summary");
      return response.data;
    },
  });

  // Export audit logs
  const exportAuditLogsMutation = useMutation({
    mutationFn: async ({
      startDate,
      endDate,
      format,
    }: {
      startDate: string;
      endDate: string;
      format?: string;
    }) => {
      const response = await apiClient.get("/audit/export", {
        params: {
          start_date: startDate,
          end_date: endDate,
          format: format || "json",
        },
      });
      return response.data;
    },
  });

  return {
    // Queries
    logs: logsData?.logs || [],
    logsTotal: logsData?.total || 0,
    isLoadingLogs,
    logsError,
    userActivity: userActivityData?.logs || [],
    isLoadingUserActivity,
    sensitiveAccess: sensitiveAccessData?.logs || [],
    isLoadingSensitiveAccess,
    failedAttempts: failedAttemptsData?.logs || [],
    isLoadingFailedAttempts,
    auditSummary,
    isLoadingSummary,

    // Mutations
    exportAuditLogs: exportAuditLogsMutation.mutate,
    isExportingAuditLogs: exportAuditLogsMutation.isPending,

    // Filters
    skip,
    setSkip,
    limit,
    setLimit,
    eventType,
    setEventType,
    resource,
    setResource,
    userId,
    setUserId,
  };
};
