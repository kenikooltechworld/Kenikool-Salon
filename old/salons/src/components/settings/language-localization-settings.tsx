import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import {
  useUserPreferences,
  useUpdateUserPreferences,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "fr", name: "Français" },
  { code: "es", name: "Español" },
  { code: "de", name: "Deutsch" },
  { code: "pt", name: "Português" },
];

const TIMEZONES = [
  { code: "Africa/Lagos", name: "Africa/Lagos (WAT)" },
  { code: "Africa/Johannesburg", name: "Africa/Johannesburg (SAST)" },
  { code: "Africa/Cairo", name: "Africa/Cairo (EET)" },
  { code: "Europe/London", name: "Europe/London (GMT/BST)" },
  { code: "Europe/Paris", name: "Europe/Paris (CET/CEST)" },
  { code: "America/New_York", name: "America/New_York (EST/EDT)" },
  { code: "America/Los_Angeles", name: "America/Los_Angeles (PST/PDT)" },
  { code: "Asia/Dubai", name: "Asia/Dubai (GST)" },
  { code: "Asia/Singapore", name: "Asia/Singapore (SGT)" },
  { code: "Australia/Sydney", name: "Australia/Sydney (AEDT/AEST)" },
];

const DATE_FORMATS = [
  { code: "DD/MM/YYYY", name: "DD/MM/YYYY (01/12/2024)" },
  { code: "MM/DD/YYYY", name: "MM/DD/YYYY (12/01/2024)" },
  { code: "YYYY-MM-DD", name: "YYYY-MM-DD (2024-12-01)" },
];

const TIME_FORMATS = [
  { code: "12h", name: "12-hour (2:30 PM)" },
  { code: "24h", name: "24-hour (14:30)" },
];

export function LanguageLocalizationSettings() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: preferences, isLoading } = useUserPreferences();

  const updatePreferencesMutation = useUpdateUserPreferences({
    onSuccess: () => {
      setSuccessMessage("Preferences updated successfully");
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to update preferences"
      );
    },
  });

  const handleUpdate = (key: string, value: string) => {
    updatePreferencesMutation.mutate({
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
        Language & Localization
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

      <div className="space-y-6">
        {/* Language */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Language
          </label>
          <div className="grid grid-cols-2 gap-2">
            {LANGUAGES.map((lang) => (
              <Button
                key={lang.code}
                variant={
                  preferences?.language === lang.code ? "default" : "outline"
                }
                onClick={() => handleUpdate("language", lang.code)}
                disabled={updatePreferencesMutation.isPending}
                className="justify-start"
              >
                {updatePreferencesMutation.isPending &&
                  preferences?.language === lang.code && (
                    <Spinner size="sm" className="mr-2" />
                  )}
                {lang.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Timezone */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Timezone
          </label>
          <div className="space-y-2">
            {TIMEZONES.map((tz) => (
              <Button
                key={tz.code}
                variant={
                  preferences?.timezone === tz.code ? "default" : "outline"
                }
                onClick={() => handleUpdate("timezone", tz.code)}
                disabled={updatePreferencesMutation.isPending}
                className="w-full justify-start"
              >
                {updatePreferencesMutation.isPending &&
                  preferences?.timezone === tz.code && (
                    <Spinner size="sm" className="mr-2" />
                  )}
                {tz.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Date Format */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Date Format
          </label>
          <div className="space-y-2">
            {DATE_FORMATS.map((format) => (
              <Button
                key={format.code}
                variant={
                  preferences?.date_format === format.code
                    ? "default"
                    : "outline"
                }
                onClick={() => handleUpdate("date_format", format.code)}
                disabled={updatePreferencesMutation.isPending}
                className="w-full justify-start"
              >
                {updatePreferencesMutation.isPending &&
                  preferences?.date_format === format.code && (
                    <Spinner size="sm" className="mr-2" />
                  )}
                {format.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Time Format */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Time Format
          </label>
          <div className="grid grid-cols-2 gap-2">
            {TIME_FORMATS.map((format) => (
              <Button
                key={format.code}
                variant={
                  preferences?.time_format === format.code
                    ? "default"
                    : "outline"
                }
                onClick={() => handleUpdate("time_format", format.code)}
                disabled={updatePreferencesMutation.isPending}
                className="justify-start"
              >
                {updatePreferencesMutation.isPending &&
                  preferences?.time_format === format.code && (
                    <Spinner size="sm" className="mr-2" />
                  )}
                {format.name}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
