import { useState, useEffect } from "react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "@/hooks/useNotifications";
import type { NotificationPreference } from "@/types/notification";
import { CheckCircleIcon, AlertCircleIcon, BellIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

export default function OwnerNotificationPreferences() {
  const { data: preferences = [], isLoading } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();
  const [localPreferences, setLocalPreferences] = useState<
    NotificationPreference[]
  >([]);
  const [showSuccess, setShowSuccess] = useState(false);
  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false);
  const [quietHoursStart, setQuietHoursStart] = useState("22:00");
  const [quietHoursEnd, setQuietHoursEnd] = useState("08:00");
  const [frequency, setFrequency] = useState<"real-time" | "hourly" | "daily">(
    "real-time",
  );

  useEffect(() => {
    if (preferences.length > 0) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

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
      setQuietHoursEnabled(false);
      setFrequency("real-time");
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
      <div className="flex items-center gap-3 mb-2">
        <BellIcon className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Notification Preferences
        </h1>
      </div>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
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
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-200">
            Failed to save preferences. Please try again.
          </p>
        </div>
      )}

      {/* Notification Types Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Notification Type
                </th>
                {channels.map((channel) => (
                  <th
                    key={channel.id}
                    className="px-6 py-3 text-center text-sm font-semibold text-gray-900 dark:text-white"
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
                  className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                >
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {type.label}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
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
                          className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
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

      {/* Quiet Hours Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quiet Hours
        </h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={quietHoursEnabled}
              onChange={(e) => setQuietHoursEnabled(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Enable quiet hours (no notifications during this time)
            </span>
          </label>
        </div>

        {quietHoursEnabled && (
          <div className="mt-4 flex items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Time
              </label>
              <input
                type="time"
                value={quietHoursStart}
                onChange={(e) => setQuietHoursStart(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                End Time
              </label>
              <input
                type="time"
                value={quietHoursEnd}
                onChange={(e) => setQuietHoursEnd(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        )}
      </div>

      {/* Notification Frequency Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Notification Frequency
        </h2>
        <div className="space-y-3">
          {(["real-time", "hourly", "daily"] as const).map((freq) => (
            <label key={freq} className="flex items-center gap-3">
              <input
                type="radio"
                name="frequency"
                value={freq}
                checked={frequency === freq}
                onChange={(e) => setFrequency(e.target.value as typeof freq)}
                className="w-4 h-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {freq === "real-time"
                  ? "Real-time (immediate notifications)"
                  : freq === "hourly"
                    ? "Hourly digest"
                    : "Daily digest"}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleResetToDefaults}
          className="px-6 py-3 rounded-lg font-semibold text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Reset to Defaults
        </button>
        <button
          onClick={handleSave}
          disabled={updatePreferences.isPending}
          className={cn(
            "px-6 py-3 rounded-lg font-semibold transition-colors",
            updatePreferences.isPending
              ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700",
          )}
        >
          {updatePreferences.isPending ? "Saving..." : "Save Preferences"}
        </button>
      </div>
    </div>
  );
}
