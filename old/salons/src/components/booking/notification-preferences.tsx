/**
 * NotificationPreferences Component
 * Allows users to configure notification settings
 * Validates: Requirements 6.5
 */
import React, { useState } from "react";
import { Bell, Mail, MessageSquare, Smartphone } from "lucide-react";
import type { NotificationPreferences as NotificationPreferencesType } from "@/lib/types/booking-enhancement";

interface NotificationPreferencesProps {
  preferences: NotificationPreferencesType;
  onSave: (preferences: Partial<NotificationPreferencesType>) => Promise<void>;
  loading?: boolean;
}

/**
 * Component for managing notification preferences
 */
export const NotificationPreferences: React.FC<
  NotificationPreferencesProps
> = ({ preferences, onSave, loading = false }) => {
  const [localPrefs, setLocalPrefs] = useState(preferences);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleToggle = (key: keyof NotificationPreferencesType) => {
    setLocalPrefs((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
    setSaved(false);
  };

  const handleChannelToggle = () => {
    // Channel preferences are managed separately in the backend
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(localPrefs);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
      <div className="flex items-center gap-2">
        <Bell className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">
          Notification Preferences
        </h2>
      </div>

      {/* Notification Types */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Notification Types</h3>
        <div className="space-y-2">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.booking_confirmation}
              onChange={() => handleToggle("booking_confirmation")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Booking Confirmation</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.booking_reminder_24h}
              onChange={() => handleToggle("booking_reminder_24h")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Reminder 24 Hours Before</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.booking_reminder_1h}
              onChange={() => handleToggle("booking_reminder_1h")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Reminder 1 Hour Before</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.cancellation_notification}
              onChange={() => handleToggle("cancellation_notification")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Cancellation Notification</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.rescheduling_notification}
              onChange={() => handleToggle("rescheduling_notification")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Rescheduling Notification</span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={localPrefs.credit_expiration_warning}
              onChange={() => handleToggle("credit_expiration_warning")}
              disabled={loading || saving}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-gray-700">Credit Expiration Warning</span>
          </label>
        </div>
      </div>

      {/* Notification Channels */}
      <div className="space-y-3 border-t border-gray-200 pt-6">
        <h3 className="font-semibold text-gray-900">Notification Channels</h3>
        <p className="text-sm text-gray-600">
          Manage your notification channels in account settings
        </p>
        <div className="space-y-2">
          <label className="flex items-center gap-3">
            <Mail className="h-4 w-4 text-gray-600" />
            <span className="text-gray-700">Email</span>
          </label>
          <label className="flex items-center gap-3">
            <MessageSquare className="h-4 w-4 text-gray-600" />
            <span className="text-gray-700">SMS</span>
          </label>
          <label className="flex items-center gap-3">
            <Smartphone className="h-4 w-4 text-gray-600" />
            <span className="text-gray-700">Push Notification</span>
          </label>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center gap-3 border-t border-gray-200 pt-6">
        <button
          onClick={handleSave}
          disabled={loading || saving}
          className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Preferences"}
        </button>
        {saved && (
          <span className="text-sm text-green-600">✓ Preferences saved</span>
        )}
      </div>
    </div>
  );
};

export default NotificationPreferences;
