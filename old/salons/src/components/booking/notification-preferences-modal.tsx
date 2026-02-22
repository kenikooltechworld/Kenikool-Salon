/**
 * NotificationPreferencesModal Component
 * Displays notification preference options and allows opt-in/opt-out
 * Validates: Requirements 6.5
 */
import React, { useState, useEffect } from "react";
import { Bell, Mail, MessageSquare, X } from "lucide-react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "../../lib/api/hooks/useNotifications";

interface NotificationPreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Component for managing notification preferences
 */
export const NotificationPreferencesModal: React.FC<
  NotificationPreferencesModalProps
> = ({ isOpen, onClose }) => {
  const { data: preferences, isLoading } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();
  const [localPrefs, setLocalPrefs] = useState<Record<string, boolean>>({});
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (preferences) {
      setLocalPrefs({
        booking_confirmation: preferences.booking_confirmation,
        booking_reminder_24h: preferences.booking_reminder_24h,
        booking_reminder_1h: preferences.booking_reminder_1h,
        booking_cancellation: preferences.booking_cancellation,
        booking_rescheduled: preferences.booking_rescheduled,
        credit_expiration: preferences.credit_expiration_warning,
        promotional: preferences.promotional_offers,
      });
    }
  }, [preferences]);

  const handleToggle = (key: string) => {
    setLocalPrefs((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updatePreferences.mutateAsync({
        booking_confirmation: localPrefs.booking_confirmation,
        booking_reminder_24h: localPrefs.booking_reminder_24h,
        booking_reminder_1h: localPrefs.booking_reminder_1h,
        booking_cancellation: localPrefs.booking_cancellation,
        booking_rescheduled: localPrefs.booking_rescheduled,
        credit_expiration_warning: localPrefs.credit_expiration,
        promotional_offers: localPrefs.promotional,
      });
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  const notificationTypes = [
    {
      key: "booking_confirmation",
      label: "Booking Confirmations",
      description: "Receive confirmation when your booking is confirmed",
      icon: Bell,
    },
    {
      key: "booking_reminder_24h",
      label: "24-Hour Reminders",
      description: "Receive reminder 24 hours before your appointment",
      icon: MessageSquare,
    },
    {
      key: "booking_reminder_1h",
      label: "1-Hour Reminders",
      description: "Receive reminder 1 hour before your appointment",
      icon: MessageSquare,
    },
    {
      key: "booking_cancellation",
      label: "Cancellation Notifications",
      description: "Receive notification when a booking is cancelled",
      icon: X,
    },
    {
      key: "booking_rescheduled",
      label: "Rescheduling Notifications",
      description: "Receive notification when a booking is rescheduled",
      icon: Bell,
    },
    {
      key: "credit_expiration",
      label: "Credit Expiration Warnings",
      description: "Receive warning when your credits are about to expire",
      icon: Mail,
    },
    {
      key: "promotional",
      label: "Promotional Offers",
      description: "Receive special offers and promotions",
      icon: Mail,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Notification Preferences
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="text-center text-sm text-gray-500">Loading...</div>
        ) : (
          <>
            {/* Notification Types */}
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {notificationTypes.map((type) => {
                const Icon = type.icon;
                const isEnabled = localPrefs[type.key];

                return (
                  <div
                    key={type.key}
                    className="flex items-start gap-3 rounded-lg border border-gray-200 p-3 hover:bg-gray-50"
                  >
                    <div className="mt-1">
                      <Icon className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">
                        {type.label}
                      </div>
                      <div className="text-sm text-gray-600">
                        {type.description}
                      </div>
                    </div>
                    <label className="relative inline-flex cursor-pointer items-center">
                      <input
                        type="checkbox"
                        checked={isEnabled || false}
                        onChange={() => handleToggle(type.key)}
                        className="peer sr-only"
                      />
                      <div className="peer h-6 w-11 rounded-full bg-gray-300 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all peer-checked:bg-blue-600 peer-checked:after:translate-x-full" />
                    </label>
                  </div>
                );
              })}
            </div>

            {/* Actions */}
            <div className="mt-6 flex gap-3 border-t border-gray-200 pt-4">
              <button
                onClick={onClose}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isSaving ? "Saving..." : "Save Preferences"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NotificationPreferencesModal;
