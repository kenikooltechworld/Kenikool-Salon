import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import {
  useUserPreferences,
  useUpdateUserPreferences,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

const FONT_SIZES = [
  { value: "small", label: "Small", size: "text-sm" },
  { value: "medium", label: "Medium", size: "text-base" },
  { value: "large", label: "Large", size: "text-lg" },
];

export function AccessibilitySettings() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: preferences, isLoading } = useUserPreferences();

  const updatePreferencesMutation = useUpdateUserPreferences({
    onSuccess: () => {
      setSuccessMessage("Accessibility settings updated successfully");
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to update accessibility settings"
      );
    },
  });

  const handleToggle = (key: string, value: boolean) => {
    updatePreferencesMutation.mutate({
      [key]: value,
    });
  };

  const handleFontSizeChange = (size: string) => {
    updatePreferencesMutation.mutate({
      font_size: size,
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
        Accessibility
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
        {/* Font Size */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Font Size
          </label>
          <div className="grid grid-cols-3 gap-2">
            {FONT_SIZES.map((size) => (
              <button
                key={size.value}
                onClick={() => handleFontSizeChange(size.value)}
                disabled={updatePreferencesMutation.isPending}
                className={`p-3 rounded-lg border transition-colors ${
                  preferences?.font_size === size.value
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-muted border-border hover:bg-muted/80"
                } disabled:opacity-50`}
              >
                <span className={size.size}>{size.label}</span>
              </button>
            ))}
          </div>
          <p className={`mt-3 ${FONT_SIZES.find((s) => s.value === preferences?.font_size)?.size}`}>
            This is a preview of your selected font size
          </p>
        </div>

        {/* High Contrast */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">High Contrast Mode</p>
            <p className="text-sm text-muted-foreground">
              Increase contrast for better visibility
            </p>
          </div>
          <Switch
            checked={preferences?.high_contrast ?? false}
            onCheckedChange={(value) =>
              handleToggle("high_contrast", value)
            }
            disabled={updatePreferencesMutation.isPending}
            className="ml-4"
          />
        </div>

        {/* Reduce Motion */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">Reduce Motion</p>
            <p className="text-sm text-muted-foreground">
              Minimize animations and transitions
            </p>
          </div>
          <Switch
            checked={preferences?.reduce_motion ?? false}
            onCheckedChange={(value) =>
              handleToggle("reduce_motion", value)
            }
            disabled={updatePreferencesMutation.isPending}
            className="ml-4"
          />
        </div>

        {/* Screen Reader Mode */}
        <div className="flex items-start justify-between p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-foreground">Screen Reader Mode</p>
            <p className="text-sm text-muted-foreground">
              Optimize for screen reader compatibility
            </p>
          </div>
          <Switch
            checked={preferences?.screen_reader ?? false}
            onCheckedChange={(value) =>
              handleToggle("screen_reader", value)
            }
            disabled={updatePreferencesMutation.isPending}
            className="ml-4"
          />
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            ℹ️ Accessibility Features
          </p>
          <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
            <li>• Font size adjustments apply across the entire application</li>
            <li>• High contrast mode improves readability for low vision users</li>
            <li>• Reduce motion disables animations for users sensitive to motion</li>
            <li>• Screen reader mode adds ARIA labels for assistive technologies</li>
          </ul>
        </div>
      </div>
    </Card>
  );
}
