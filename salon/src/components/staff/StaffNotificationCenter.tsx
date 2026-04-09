import { useState } from "react";
import {
  useNotifications,
  useClearAllNotifications,
  useUnreadNotificationCount,
} from "@/hooks/useNotifications";
import NotificationList from "@/components/notifications/NotificationList";
import { Trash2Icon, XIcon, FilterIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface StaffNotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const STAFF_NOTIFICATION_TYPES = [
  { value: "appointment_reminder_24h", label: "Appointment Reminders" },
  { value: "shift_assigned", label: "Shift Assignments" },
  { value: "shift_reminder", label: "Shift Reminders" },
  { value: "time_off_approved", label: "Time Off Approved" },
  { value: "time_off_rejected", label: "Time Off Denied" },
  { value: "commission_payment", label: "Commission Payments" },
];

export default function StaffNotificationCenter({
  isOpen,
  onClose,
  className,
}: StaffNotificationCenterProps) {
  const [selectedType, setSelectedType] = useState<string | undefined>();
  const [showFilters, setShowFilters] = useState(false);
  const { data: notifications = [] } = useNotifications({ type: selectedType });
  const { data: unreadCount = 0 } = useUnreadNotificationCount();
  const clearAll = useClearAllNotifications();

  const handleClearAll = () => {
    if (
      window.confirm(
        "Are you sure you want to clear all notifications? This action cannot be undone.",
      )
    ) {
      clearAll.mutate();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={cn("fixed inset-0 z-50 bg-black/50", className)}>
      <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-card shadow-lg flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Notifications
            </h2>
            {unreadCount > 0 && (
              <p className="text-sm text-muted-foreground">
                {unreadCount} unread
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                "p-2 rounded-lg transition-colors",
                showFilters
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted",
              )}
              title="Filter notifications"
            >
              <FilterIcon className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-muted-foreground hover:bg-muted rounded-lg transition-colors"
            >
              <XIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="p-4 border-b border-border bg-muted/50">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedType(undefined)}
                className={cn(
                  "px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
                  !selectedType
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground hover:bg-muted border border-border",
                )}
              >
                All
              </button>
              {STAFF_NOTIFICATION_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setSelectedType(type.value)}
                  className={cn(
                    "px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
                    selectedType === type.value
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-foreground hover:bg-muted border border-border",
                  )}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto p-4">
          <NotificationList limit={50} />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border bg-muted/50">
          <button
            onClick={handleClearAll}
            disabled={notifications.length === 0 || clearAll.isPending}
            className={cn(
              "w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-colors",
              notifications.length === 0 || clearAll.isPending
                ? "bg-muted text-muted-foreground cursor-not-allowed"
                : "bg-destructive text-destructive-foreground hover:bg-destructive/90",
            )}
          >
            <Trash2Icon className="w-4 h-4" />
            Clear All Notifications
          </button>
        </div>
      </div>
    </div>
  );
}
