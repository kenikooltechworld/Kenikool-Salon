import { useState, useEffect } from "react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "@/hooks/useNotifications";
import { CheckCircleIcon, AlertCircleIcon, RefreshCwIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";

export default function NotificationPreferences() {
  const { data: preferences = [], isLoading, refetch } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();
  const [localPreferences, setLocalPreferences] = useState<any[]>([]);
  const [showSuccess, setShowSuccess] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    if (preferences.length > 0) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

  const notificationTypes = [
    "appointment_confirmation",
    "appointment_reminder_24h",
    "appointment_reminder_1h",
    "appointment_cancelled",
    "appointment_completed",
    "payment_receipt",
    "shift_assigned",
    "time_off_approved",
    "time_off_rejected",
  ];

  const channels = ["email", "sms", "push", "in_app"];

  const handleToggle = (index: number) => {
    const updated = [...localPreferences];
    updated[index].enabled = !updated[index].enabled;
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

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-5 w-96" />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="px-6 py-3 text-left">
                    <Skeleton className="h-4 w-32" />
                  </th>
                  {[...Array(4)].map((_, i) => (
                    <th
                      key={i}
                      className="px-6 py-3 text-center"
                    >
                      <Skeleton className="h-4 w-12 mx-auto" />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[...Array(5)].map((_, i) => (
                  <tr
                    key={i}
                    className="border-b border-gray-200 dark:border-gray-700"
                  >
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-40" />
                    </td>
                    {[...Array(4)].map((_, j) => (
                      <td key={j} className="px-6 py-4 text-center">
                        <Skeleton className="h-5 w-5 mx-auto" />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Notification Preferences
        </h1>
      </div>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Manage how and when you receive notifications
      </p>

      {showSuccess && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-800 dark:text-green-200">
            Preferences saved successfully!
          </p>
        </div>
      )}

      {updatePreferences.isError && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-200">
            Failed to save preferences. Please try again.
          </p>
        </div>
      )}

      {/* Preferences Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Notification Type
                </th>
                {channels.map((channel) => (
                  <th
                    key={channel}
                    className="px-6 py-3 text-center text-sm font-semibold text-gray-900 dark:text-white"
                  >
                    {channel.charAt(0).toUpperCase() + channel.slice(1)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {notificationTypes.map((type) => (
                <tr
                  key={type}
                  className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                    {type.replace(/_/g, " ")}
                  </td>
                  {channels.map((channel) => {
                    const pref = localPreferences.find(
                      (p) =>
                        p.notification_type === type && p.channel === channel,
                    );
                    return (
                      <td key={channel} className="px-6 py-4 text-center">
                        <input
                          type="checkbox"
                          checked={pref?.enabled ?? true}
                          onChange={() => {
                            const index = localPreferences.findIndex(
                              (p) =>
                                p.notification_type === type &&
                                p.channel === channel,
                            );
                            if (index !== -1) {
                              handleToggle(index);
                            }
                          }}
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

      {/* Save Button */}
      <div className="mt-6 flex justify-end">
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
