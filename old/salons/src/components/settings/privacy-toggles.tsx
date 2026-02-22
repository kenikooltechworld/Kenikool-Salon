import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import {
  usePrivacySettings,
  useUpdatePrivacySettings,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

export function PrivacyToggles() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: privacySettings, isLoading } = usePrivacySettings();

  const updatePrivacyMutation = useUpdatePrivacySettings({
    onSuccess: () => {
      setSuccessMessage("Privacy settings updated successfully");
      queryClient.invalidateQueries({ queryKey: ["privacy-settings"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to update privacy settings"
      );
    },
  });

  const handleToggle = (key: string, value: boolean) => {
    updatePrivacyMutation.mutate({
      [key]: value,
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

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Privacy Controls
      </h2>

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

      <div className="space-y-4">
        {/* Analytics Toggle */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">Analytics</p>
            <p className="text-sm text-muted-foreground">
              Allow us to collect usage data to improve your experience
            </p>
          </div>
          <Switch
            checked={privacySettings?.analytics_enabled ?? true}
            onCheckedChange={(value) =>
              handleToggle("analytics_enabled", value)
            }
            disabled={updatePrivacyMutation.isPending}
            className="ml-4"
          />
        </div>

        {/* Marketing Emails Toggle */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">Marketing Emails</p>
            <p className="text-sm text-muted-foreground">
              Receive promotional emails and special offers
            </p>
          </div>
          <Switch
            checked={privacySettings?.marketing_emails ?? true}
            onCheckedChange={(value) =>
              handleToggle("marketing_emails", value)
            }
            disabled={updatePrivacyMutation.isPending}
            className="ml-4"
          />
        </div>

        {/* Third-Party Sharing Toggle */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">Third-Party Sharing</p>
            <p className="text-sm text-muted-foreground">
              Allow sharing of your data with trusted partners
            </p>
          </div>
          <Switch
            checked={privacySettings?.third_party_sharing ?? false}
            onCheckedChange={(value) =>
              handleToggle("third_party_sharing", value)
            }
            disabled={updatePrivacyMutation.isPending}
            className="ml-4"
          />
        </div>
      </div>
    </Card>
  );
}
