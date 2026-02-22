import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import {
  LockIcon,
  MonitorIcon,
  LogOutIcon,
  EditIcon,
  TrashIcon,
  MailIcon,
  PhoneIcon,
  SettingsIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useAuditLog } from "@/lib/api/hooks/useSettings";
import type { LoginActivity } from "@/lib/api/hooks/useSettings";

export function AuditLogTimeline() {
  const { data: events = [], isLoading } = useAuditLog();

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case "login":
        return <MonitorIcon size={16} />;
      case "logout":
        return <LogOutIcon size={16} />;
      case "password_change":
        return <LockIcon size={16} />;
      case "2fa_enabled":
      case "2fa_disabled":
        return <EditIcon size={16} />;
      case "account_deletion_requested":
        return <TrashIcon size={16} />;
      case "email_changed":
        return <MailIcon size={16} />;
      case "phone_verified":
        return <PhoneIcon size={16} />;
      case "settings_updated":
        return <SettingsIcon size={16} />;
      default:
        return <SettingsIcon size={16} />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case "login":
        return "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100";
      case "logout":
        return "bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100";
      case "password_change":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100";
      case "2fa_enabled":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100";
      case "2fa_disabled":
        return "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-100";
      case "account_deletion_requested":
        return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100";
      case "email_changed":
        return "bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-100";
      case "phone_verified":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100";
      case "settings_updated":
        return "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100";
      default:
        return "bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100";
    }
  };

  const formatEventType = (eventType: string) => {
    return eventType
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
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

  if (events.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">No audit log events yet.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Security Events
      </h2>

      <div className="space-y-4">
        {events.map((event: LoginActivity, index: number) => (
          <div key={event.id} className="flex gap-4">
            {/* Timeline line */}
            {index !== events.length - 1 && (
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${getEventColor(
                    event.event_type
                  )}`}
                >
                  {getEventIcon(event.event_type)}
                </div>
                <div className="w-0.5 h-12 bg-border mt-2" />
              </div>
            )}

            {/* Last item - no line */}
            {index === events.length - 1 && (
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${getEventColor(
                    event.event_type
                  )}`}
                >
                  {getEventIcon(event.event_type)}
                </div>
              </div>
            )}

            {/* Event content */}
            <div className="flex-1 pt-1">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-foreground">
                    {formatEventType(event.event_type)}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(event.timestamp)}
                  </p>
                </div>

                {event.flagged && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded text-xs font-medium">
                    <AlertTriangleIcon size={12} />
                    Suspicious
                  </div>
                )}
              </div>

              <div className="mt-2 text-sm text-muted-foreground space-y-1">
                {event.device && <p>Device: {event.device}</p>}
                {event.browser && <p>Browser: {event.browser}</p>}
                {event.ip_address && <p>IP: {event.ip_address}</p>}
                {event.location && <p>Location: {event.location}</p>}
                {!event.success && (
                  <p className="text-red-600 dark:text-red-400 font-medium">
                    Failed attempt
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
