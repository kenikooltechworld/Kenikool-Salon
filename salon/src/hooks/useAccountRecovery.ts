import { useState } from "react";
import { apiClient } from "@/lib/utils/api";

interface RecoveryStatus {
  is_deleted: boolean;
  days_remaining?: number;
  can_recover: boolean;
  recovery_expires_at?: string;
}

export function useAccountRecovery() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recoverAccount = async (token: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post("/api/tenants/recover", {
        recovery_token: token,
      });

      return {
        success: response.data.success,
        message: response.data.message,
        tenant_id: response.data.tenant_id,
      };
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || "Recovery failed";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const getRecoveryStatus = async (
    tenantId: string,
  ): Promise<RecoveryStatus | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(
        `/api/tenants/recovery-status/${tenantId}`,
      );
      return response.data;
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Failed to get recovery status";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    recoverAccount,
    getRecoveryStatus,
    isLoading,
    error,
  };
}
