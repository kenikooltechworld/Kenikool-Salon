import { NotificationSettings } from "@/components/notifications/notification-settings";

export default function NotificationSettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Notification Settings
        </h1>
        <p className="text-muted-foreground">
          Manage how you receive notifications
        </p>
      </div>
      <NotificationSettings />
    </div>
  );
}
