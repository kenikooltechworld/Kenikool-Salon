import { useState, useEffect } from "react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "@/hooks/useNotifications";
import { cn } from "@/lib/utils/cn";
import {
  BellIcon,
  MailIcon,
  MessageSquareIcon,
  PhoneIcon,
} from "@/components/icons";

const STAFF_NOTIFICATION_TYPES = [
  {
    type: "appointment_reminder_24h",
    label: "Appointment Reminders (24 hours)",
    description: "Get notified 24 hours before your appointments",
  },
  {
    type: "appointment_reminder_1h",
    label: "Appointment Reminders (1 hour)",
    description: "Get notified 1 hour before your appointments",
  },
  {
    type: "shift_assigned",
    label: "Shift Assignments",
    description: "Get notified when shifts are assigned to you",
  },
  {
    type: "shift_reminder",
    label: "Shift Reminders",
    description: "Get notified at the start of your shifts",
  },
  {
    type: "time_off_approved",
    label: "Time Off Approved",
    description: "Get notified when your time off requests are approved",
  },
  {
    type: "time_off_rejected",
    label: "Time Off Denied",
    description: "Get notified when your time off requests are denied",
  },
  {
    type: "commission_payment",
    label: "Commission Payments",
    description: "Get notified when commission payments are processed",
  },
];

type NotificationChannel = "in_app" | "email" | "sms" | "push";

const CHANNELS: Array<{
  value: NotificationChannel;
  label: string;
  icon: typeof BellIcon;
}> = [
  { value: "in_app", label: "In-App", icon: BellIcon },
  { value: "email", label: "Email", icon: MailIcon },
  { value: "sms", label: "SMS", icon: MessageSquareIcon },
  { value: "push", label: "Push", icon: PhoneIcon },
];

export default function StaffNotificationPreferences() {
  const { data: preferences = [], isLoading } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();
  const [localPreferences, setLocalPreferences] = useState<
    Record<string, Record<string, boolean>>
  >({});

  // Initialize local preferences from API data
  useEffect(() => {
    if (preferences.length > 0) {
      const prefs: Record<string, Record<string, boolean>> = {};
      preferences.forEach((pref: any) => {
        if (!prefs[pref.notification_type]) {
          prefs[pref.notification_type] = {};
        }
        prefs[pref.notification_type][pref.channel] = pref.enabled;
      });
      setLocalPreferences(prefs);
    } else {
      // Initialize with defaults (all enabled)
      const defaultPrefs: Record<string, Record<string, boolean>> = {};
      STAFF_NOTIFICATION_TYPES.forEach((type) => {
        defaultPrefs[type.type] = {};
        CHANNELS.forEach((channel) => {
          defaultPrefs[type.type][channel.value] = true;
        });
      });
      setLocalPreferences(defaultPrefs);
    }
  }, [preferences]);

  const handleToggle = async (
    notificationType: string,
    channel: "in_app" | "email" | "sms" | "push",
  ) => {
    const currentValue = localPreferences[notificationType]?.[channel] ?? true;
    const newValue = !currentValue;

    // Update local state immediately for responsive UI
    setLocalPreferences((prev) => ({
      ...prev,
      [notificationType]: {
        ...prev[notificationType],
        [channel]: newValue,
      },
    }));

    // Update backend
    try {
      await updatePreferences.mutateAsync([
        {
          notification_type: notificationType,
          channel,
          enabled: newValue,
        },
      ]);
    } catch (error) {
      // Revert on error
      setLocalPreferences((prev) => ({
        ...prev,
        [notificationType]: {
          ...prev[notificationType],
          [channel]: currentValue,
        },
      }));
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-muted rounded animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Notification Preferences
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Choose how you want to be notified about appointments, shifts, and
          more
        </p>
      </div>

      <div className="space-y-4">
        {STAFF_NOTIFICATION_TYPES.map((notificationType) => (
          <div
            key={notificationType.type}
            className="bg-card border border-border rounded-lg p-4"
          >
            <div className="mb-3">
              <h3 className="font-semibold text-foreground">
                {notificationType.label}
              </h3>
              <p className="text-sm text-muted-foreground">
                {notificationType.description}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {CHANNELS.map((channel) => {
                const Icon = channel.icon;
                const isEnabled =
                  localPreferences[notificationType.type]?.[channel.value] ??
                  true;

                return (
                  <button
                    key={channel.value}
                    onClick={() =>
                      handleToggle(notificationType.type, channel.value)
                    }
                    className={cn(
                      "flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors",
                      isEnabled
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-muted border-border text-muted-foreground",
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{channel.label}</span>
                    <div
                      className={cn(
                        "ml-auto w-4 h-4 rounded-full border-2 flex items-center justify-center",
                        isEnabled
                          ? "bg-primary border-primary"
                          : "bg-background border-border",
                      )}
                    >
                      {isEnabled && (
                        <div className="w-2 h-2 bg-primary-foreground rounded-full" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {updatePreferences.isError && (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
          <p className="text-sm text-destructive">
            Failed to update preferences. Please try again.
          </p>
        </div>
      )}
    </div>
  );
}
