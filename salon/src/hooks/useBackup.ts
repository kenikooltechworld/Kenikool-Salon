import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useState } from "react";

export interface Backup {
  id: string;
  backup_type: "full" | "incremental" | "differential";
  status: "pending" | "in_progress" | "completed" | "failed";
  s3_location: string;
  s3_key: string;
  size_bytes?: number;
  file_count?: number;
  checksum?: string;
  encryption_key_id?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  retention_days: number;
  is_verified: boolean;
  verified_at?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface BackupRestore {
  id: string;
  backup_id: string;
  restore_type: "full" | "point_in_time" | "selective";
  status: "pending" | "in_progress" | "completed" | "failed";
  restore_point?: string;
  target_database?: string;
  restored_records?: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  verified_at?: string;
  is_verified: boolean;
  created_at: string;
}

export interface BackupSchedule {
  id: string;
  backup_frequency: "daily" | "weekly" | "monthly";
  backup_time: string;
  retention_days: number;
  is_enabled: boolean;
  last_backup_at?: string;
  next_backup_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BackupStatistics {
  total_backups: number;
  completed_backups: number;
  failed_backups: number;
  total_size_bytes: number;
  last_backup_at?: string;
  last_backup_size_bytes?: number;
}

export const useBackup = () => {
  const queryClient = useQueryClient();
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(100);

  // List backups
  const {
    data: backupsData,
    isLoading: isLoadingBackups,
    error: backupsError,
  } = useQuery({
    queryKey: ["backups", skip, limit],
    queryFn: async () => {
      const response = await apiClient.get("/backups", {
        params: { skip, limit },
      });
      return response.data;
    },
  });

  // Get backup statistics
  const { data: backupStats, isLoading: isLoadingStats } = useQuery({
    queryKey: ["backups", "statistics"],
    queryFn: async () => {
      const response = await apiClient.get("/backups/statistics");
      return response.data;
    },
  });

  // Get backup schedule
  const { data: backupSchedule, isLoading: isLoadingSchedule } = useQuery({
    queryKey: ["backups", "schedule"],
    queryFn: async () => {
      const response = await apiClient.get("/backups/schedule");
      return response.data;
    },
  });

  // List restores
  const { data: restoresData, isLoading: isLoadingRestores } = useQuery({
    queryKey: ["backups", "restores", skip, limit],
    queryFn: async () => {
      const response = await apiClient.get("/backups/restores", {
        params: { skip, limit },
      });
      return response.data;
    },
  });

  // Create backup
  const createBackupMutation = useMutation({
    mutationFn: async (
      backupType: "full" | "incremental" | "differential" = "full",
    ) => {
      const response = await apiClient.post("/backups", {
        backup_type: backupType,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups"] });
    },
  });

  // Verify backup
  const verifyBackupMutation = useMutation({
    mutationFn: async (backupId: string) => {
      const response = await apiClient.post(`/backups/${backupId}/verify`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups"] });
    },
  });

  // Create restore
  const createRestoreMutation = useMutation({
    mutationFn: async ({
      backupId,
      restoreType,
      restorePoint,
    }: {
      backupId: string;
      restoreType: "full" | "point_in_time" | "selective";
      restorePoint?: string;
    }) => {
      const response = await apiClient.post(`/backups/${backupId}/restore`, {
        restore_type: restoreType,
        restore_point: restorePoint,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups", "restores"] });
    },
  });

  // Verify restore
  const verifyRestoreMutation = useMutation({
    mutationFn: async (restoreId: string) => {
      const response = await apiClient.post(
        `/backups/restores/${restoreId}/verify`,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups", "restores"] });
    },
  });

  // Update backup schedule
  const updateScheduleMutation = useMutation({
    mutationFn: async ({
      backupFrequency,
      backupTime,
      retentionDays,
      isEnabled,
    }: {
      backupFrequency?: "daily" | "weekly" | "monthly";
      backupTime?: string;
      retentionDays?: number;
      isEnabled?: boolean;
    }) => {
      const response = await apiClient.put("/backups/schedule", {
        backup_frequency: backupFrequency,
        backup_time: backupTime,
        retention_days: retentionDays,
        is_enabled: isEnabled,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups", "schedule"] });
    },
  });

  // Download backup
  const downloadBackupMutation = useMutation({
    mutationFn: async (backupId: string) => {
      const response = await apiClient.get(`/backups/${backupId}/download`, {
        responseType: "blob",
      });
      return response.data;
    },
  });

  return {
    // Queries
    backups: backupsData?.backups || [],
    backupsTotal: backupsData?.total || 0,
    isLoadingBackups,
    backupsError,
    backupStats,
    isLoadingStats,
    backupSchedule,
    isLoadingSchedule,
    restores: restoresData?.restores || [],
    restoresTotal: restoresData?.total || 0,
    isLoadingRestores,

    // Mutations
    createBackup: createBackupMutation.mutate,
    isCreatingBackup: createBackupMutation.isPending,
    verifyBackup: verifyBackupMutation.mutate,
    isVerifyingBackup: verifyBackupMutation.isPending,
    createRestore: createRestoreMutation.mutate,
    isCreatingRestore: createRestoreMutation.isPending,
    verifyRestore: verifyRestoreMutation.mutate,
    isVerifyingRestore: verifyRestoreMutation.isPending,
    updateSchedule: updateScheduleMutation.mutate,
    isUpdatingSchedule: updateScheduleMutation.isPending,
    downloadBackup: downloadBackupMutation.mutate,
    isDownloadingBackup: downloadBackupMutation.isPending,

    // Pagination
    skip,
    setSkip,
    limit,
    setLimit,
  };
};
