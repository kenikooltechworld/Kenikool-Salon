import { useState, useEffect } from "react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "@/hooks/useNotifications";
import type { NotificationPreference } from "@/types/notification";
import { CheckCircleIcon, AlertCircleIcon, BellIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";
import { useToast } from "@/components/ui/toast";
import { usePageRefresh } from "@/contexts/PageRefreshContext";

export default function OwnerNotificationPreferences() {
  const { data: preferences = [], isLoading, refetch } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();
  const [localPreferences, setLocalPreferences] = useState<
    NotificationPreference[]
  >([]);
  const [showSuccess, setShowSuccess] = useState(false);
  const { showToast } = useToast();
  const { setRefreshHandler } = usePageRefresh();

  useEffect(() => {
    if (preferences.length > 0) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

  useEffect(() => {
    setRefreshHandler(() => refetch);
  }, [refetch, setRefreshHandler]);

  // Owner-specific notification types
  const ownerNotificationTypes = [
    {
      id: "new_appointment",
      label: "New Appointment",
      description: "When a new appointment is booked",
    },
    {
      id: "payment_received",
      label: "Payment Received",
      description: "When a payment is successfully processed",
    },
    {
      id: "payment_failed",
      label: "Payment Failed",
      description: "When a payment fails to process",
    },
    {
      id: "staff_alert",
      label: "Staff Alert",
      description: "Staff-related alerts (no-show, call-in sick, etc.)",
    },
    {
      id: "inventory_alert",
      label: "Inventory Alert",
      description: "Low stock or expiring inventory alerts",
    },
    {
      id: "customer_review",
      label: "Customer Review",
      description: "When a customer leaves a review",
    },
  ];

  const channels: Array<{
    id: "email" | "sms" | "push" | "in_app";
    label: string;
  }> = [
    { id: "in_app", label: "In-App" },
    { id: "email", label: "Email" },
    { id: "sms", label: "SMS" },
  ];

  const handleToggle = (
    notificationType: string,
    channel: "email" | "sms" | "push" | "in_app",
  ) => {
    const updated = localPreferences.map((pref) => {
      if (
        pref.notification_type === notificationType &&
        pref.channel === channel
      ) {
        return { ...pref, enabled: !pref.enabled };
      }
      return pref;
    });
    setLocalPreferences(updated);
  };

  const handleSave = () => {
    updatePreferences.mutate(localPreferences, {
      onSuccess: () => {
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      },
    });
  };

  const handleResetToDefaults = () => {
    if (confirm("Are you sure you want to reset to default preferences?")) {
      const defaults = ownerNotificationTypes.flatMap((type) =>
        channels.map(
          (channel) =>
            ({
              notification_type: type.id,
              channel: channel.id,
              enabled: true,
            }) as NotificationPreference,
        ),
      );
      setLocalPreferences(defaults);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <BellIcon className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-foreground">
            Notification Preferences
          </h1>
        </div>
      </div>
      <p className="text-muted-foreground mb-6">
        Manage how and when you receive notifications about your business
      </p>

      {showSuccess && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircleIcon className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
          <p className="text-sm text-green-800 dark:text-green-200">
            Preferences saved successfully!
          </p>
        </div>
      )}

      {updatePreferences.isError && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
          <p className="text-sm text-destructive">
            Failed to save preferences. Please try again.
          </p>
        </div>
      )}

      {/* Notification Types Table */}
      <div className="bg-background rounded-lg border border-border overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted">
                <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">
                  Notification Type
                </th>
                {channels.map((channel) => (
                  <th
                    key={channel.id}
                    className="px-6 py-3 text-center text-sm font-semibold text-foreground"
                  >
                    {channel.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ownerNotificationTypes.map((type) => (
                <tr
                  key={type.id}
                  className="border-b border-border hover:bg-muted"
                >
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {type.label}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {type.description}
                      </p>
                    </div>
                  </td>
                  {channels.map((channel) => {
                    const pref = localPreferences.find(
                      (p) =>
                        p.notification_type === type.id &&
                        p.channel === channel.id,
                    );
                    return (
                      <td key={channel.id} className="px-6 py-4 text-center">
                        <input
                          type="checkbox"
                          checked={pref?.enabled ?? true}
                          onChange={() => handleToggle(type.id, channel.id)}
                          className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleResetToDefaults}
          className="px-6 py-3 rounded-lg font-semibold text-foreground border border-border hover:bg-muted transition-colors"
        >
          Reset to Defaults
        </button>
        <button
          onClick={handleSave}
          disabled={updatePreferences.isPending}
          className={cn(
            "px-6 py-3 rounded-lg font-semibold transition-colors",
            updatePreferences.isPending
              ? "bg-muted text-muted-foreground cursor-not-allowed"
              : "bg-primary text-primary-foreground hover:bg-primary/90",
          )}
        >
          {updatePreferences.isPending ? "Saving..." : "Save Preferences"}
        </button>
      </div>
    </div>
  );
}
