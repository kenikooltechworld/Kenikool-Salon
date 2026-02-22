import { useState } from "react";
import {
  useNotifications,
  useClearAllNotifications,
} from "@/hooks/useNotifications";
import NotificationList from "./NotificationList";
import { Trash2Icon, XIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

export default function NotificationCenter({
  isOpen,
  onClose,
  className,
}: NotificationCenterProps) {
  const [selectedType, setSelectedType] = useState<string | undefined>();
  const { data: notifications = [] } = useNotifications({ type: selectedType });
  const clearAll = useClearAllNotifications();

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

  const handleClearAll = () => {
    if (window.confirm("Are you sure you want to clear all notifications?")) {
      clearAll.mutate();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={cn("fixed inset-0 z-50 bg-black/50", className)}>
      <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-white dark:bg-gray-900 shadow-lg flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Notifications
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <XIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedType(undefined)}
              className={cn(
                "px-3 py-1 rounded-full text-sm font-medium transition-colors",
                !selectedType
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600",
              )}
            >
              All
            </button>
            {notificationTypes.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={cn(
                  "px-3 py-1 rounded-full text-sm font-medium transition-colors",
                  selectedType === type
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600",
                )}
              >
                {type.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto p-4">
          <NotificationList limit={50} />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleClearAll}
            disabled={notifications.length === 0 || clearAll.isPending}
            className={cn(
              "w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors",
              notifications.length === 0 || clearAll.isPending
                ? "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                : "bg-red-600 text-white hover:bg-red-700",
            )}
          >
            <Trash2Icon className="w-4 h-4" />
            Clear All
          </button>
        </div>
      </div>
    </div>
  );
}
