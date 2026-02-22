import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import {
  usePrivacySettings,
  useUpdatePrivacySettings,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

const RETENTION_OPTIONS = [
  { value: 30, label: "30 days" },
  { value: 90, label: "90 days" },
  { value: 180, label: "6 months" },
  { value: 365, label: "1 year" },
  { value: 730, label: "2 years" },
  { value: 1095, label: "3 years" },
];

export function DataRetentionSettings() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: privacySettings, isLoading } = usePrivacySettings();

  const updatePrivacyMutation = useUpdatePrivacySettings({
    onSuccess: () => {
      setSuccessMessage("Data retention settings updated successfully");
      queryClient.invalidateQueries({ queryKey: ["privacy-settings"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to update data retention settings"
      );
    },
  });

  const handleRetentionChange = (days: number) => {
    updatePrivacyMutation.mutate({
      data_retention_days: days,
    });
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  const currentRetention = privacySettings?.data_retention_days || 365;

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-2">
        Data Retention
      </h2>
      <p className="text-sm text-muted-foreground mb-6">
        Choose how long we keep your data after you delete it
      </p>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      <div className="space-y-2">
        {RETENTION_OPTIONS.map((option) => (
          <Button
            key={option.value}
            variant={
              currentRetention === option.value ? "default" : "outline"
            }
            onClick={() => handleRetentionChange(option.value)}
            disabled={updatePrivacyMutation.isPending}
            className="w-full justify-start"
          >
            {updatePrivacyMutation.isPending &&
              currentRetention === option.value && (
                <Spinner size="sm" className="mr-2" />
              )}
            {option.label}
          </Button>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-xs font-medium text-blue-900 dark:text-blue-100 mb-2">
          ℹ️ About Data Retention
        </p>
        <p className="text-xs text-blue-800 dark:text-blue-200">
          After you delete your account, we'll keep your data for the selected
          period before permanently removing it. This allows you to recover your
          account if you change your mind.
        </p>
      </div>
    </Card>
  );
}
