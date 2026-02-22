import { useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CheckIcon,
  AlertTriangleIcon,
  BellIcon,
  MailIcon,
  PhoneIcon,
} from "@/components/icons";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
  type NotificationChannelPreferences,
} from "@/lib/api/hooks/useNotificationPreferences";
import { getNotificationSound } from "@/lib/utils/notification-sound";
import { toast } from "@/lib/utils/toast";

export function NotificationSettings() {
  const { data: preferences, isLoading, error } = useNotificationPreferences();
  const updatePreferences = useUpdateNotificationPreferences();

  const notificationSound = getNotificationSound();

  // Show toast on successful update
  useEffect(() => {
    if (updatePreferences.isSuccess) {
      toast.success("Notification preferences updated successfully");
    }
  }, [updatePreferences.isSuccess]);

  // Show toast on error
  useEffect(() => {
    if (updatePreferences.isError) {
      toast.error("Failed to update preferences. Please try again.");
    }
  }, [updatePreferences.isError]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading preferences</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  if (!preferences) {
    return null;
  }

  const handleChannelToggle = (
    notifType: keyof typeof preferences.preferences,
    channel: keyof NotificationChannelPreferences
  ) => {
    const updated = {
      ...preferences,
      preferences: {
        ...preferences.preferences,
        [notifType]: {
          ...preferences.preferences[notifType],
          [channel]: !preferences.preferences[notifType][channel],
        },
      },
    };

    updatePreferences.mutate({
      preferences: updated.preferences,
    });
  };

  const handleSoundToggle = () => {
    const newValue = !preferences.sound_enabled;
    notificationSound.setSoundEnabled(newValue);
    updatePreferences.mutate({
      sound_enabled: newValue,
    });
  };

  const handleQuietHoursToggle = () => {
    updatePreferences.mutate({
      quiet_hours_enabled: !preferences.quiet_hours_enabled,
    });
  };

  const handleQuietHoursChange = (start: string, end: string) => {
    updatePreferences.mutate({
      quiet_hours_start: start,
      quiet_hours_end: end,
    });
  };

  const testSound = () => {
    notificationSound.play();
  };

  const notificationTypes = [
    {
      key: "booking" as const,
      label: "Bookings",
      description: "New bookings and updates",
    },
    {
      key: "payment" as const,
      label: "Payments",
      description: "Payment confirmations",
    },
    {
      key: "review" as const,
      label: "Reviews",
      description: "New customer reviews",
    },
    {
      key: "inventory" as const,
      label: "Inventory",
      description: "Low stock alerts",
    },
    {
      key: "system" as const,
      label: "System",
      description: "System notifications",
    },
    {
      key: "general" as const,
      label: "General",
      description: "General updates",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Sound Settings */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Sound</h3>
            <p className="text-sm text-muted-foreground">
              Play a sound when you receive notifications
            </p>
          </div>
          <Switch
            checked={preferences.sound_enabled}
            onChange={handleSoundToggle}
          />
        </div>
        {preferences.sound_enabled && (
          <Button size="sm" variant="outline" onClick={testSound}>
            Test Sound
          </Button>
        )}
      </Card>

      {/* Quiet Hours */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Quiet Hours
            </h3>
            <p className="text-sm text-muted-foreground">
              Mute notifications during specific hours
            </p>
          </div>
          <Switch
            checked={preferences.quiet_hours_enabled}
            onChange={handleQuietHoursToggle}
          />
        </div>
        {preferences.quiet_hours_enabled && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground">
                Start Time
              </label>
              <Input
                type="time"
                value={preferences.quiet_hours_start || "22:00"}
                onChange={(e) =>
                  handleQuietHoursChange(
                    e.target.value,
                    preferences.quiet_hours_end || "08:00"
                  )
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">
                End Time
              </label>
              <Input
                type="time"
                value={preferences.quiet_hours_end || "08:00"}
                onChange={(e) =>
                  handleQuietHoursChange(
                    preferences.quiet_hours_start || "22:00",
                    e.target.value
                  )
                }
              />
            </div>
          </div>
        )}
      </Card>

      {/* Notification Type Preferences */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Notification Preferences
        </h3>
        <div className="space-y-6">
          {notificationTypes.map((type) => (
            <div
              key={type.key}
              className="border-b border-[var(--border)] pb-4 last:border-0"
            >
              <div className="mb-3">
                <h4 className="font-medium text-foreground">{type.label}</h4>
                <p className="text-sm text-muted-foreground">
                  {type.description}
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex items-center gap-2">
                  <Switch
                    checked={preferences.preferences[type.key].in_app}
                    onChange={() => handleChannelToggle(type.key, "in_app")}
                  />
                  <div className="flex items-center gap-1">
                    <BellIcon size={16} />
                    <span className="text-sm">In-App</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={preferences.preferences[type.key].email}
                    onChange={() => handleChannelToggle(type.key, "email")}
                  />
                  <div className="flex items-center gap-1">
                    <MailIcon size={16} />
                    <span className="text-sm">Email</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={preferences.preferences[type.key].sms}
                    onChange={() => handleChannelToggle(type.key, "sms")}
                  />
                  <div className="flex items-center gap-1">
                    <PhoneIcon size={16} />
                    <span className="text-sm">SMS</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={preferences.preferences[type.key].push}
                    onChange={() => handleChannelToggle(type.key, "push")}
                  />
                  <div className="flex items-center gap-1">
                    <BellIcon size={16} />
                    <span className="text-sm">Push</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
