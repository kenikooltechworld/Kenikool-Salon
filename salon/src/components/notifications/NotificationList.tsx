import {
  useNotifications,
  useMarkNotificationRead,
  useDeleteNotification,
} from "@/hooks/useNotifications";
import type { Notification } from "@/types/notification";
import { formatDistanceToNow } from "@/lib/utils/date";
import { Trash2Icon, CheckIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface NotificationListProps {
  limit?: number;
  onNotificationClick?: (notification: Notification) => void;
}

export default function NotificationList({
  limit = 10,
  onNotificationClick,
}: NotificationListProps) {
  const {
    data: notifications = [],
    isLoading,
    error,
  } = useNotifications({ limit });
  const markAsRead = useMarkNotificationRead();
  const deleteNotification = useDeleteNotification();

  const handleMarkAsRead = (notification: Notification) => {
    if (!notification.is_read) {
      markAsRead.mutate(notification.id);
    }
  };

  const handleDelete = (notificationId: string) => {
    deleteNotification.mutate(notificationId);
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-600 dark:text-red-400">
        Failed to load notifications
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 dark:text-gray-400">
        <p>No notifications yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={cn(
            "p-4 rounded-lg border transition-colors cursor-pointer",
            notification.is_read
              ? "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
              : "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
          )}
          onClick={() => {
            handleMarkAsRead(notification);
            onNotificationClick?.(notification);
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {notification.subject && (
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {notification.subject}
                </h3>
              )}
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {notification.content}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                {formatDistanceToNow(new Date(notification.created_at), {
                  addSuffix: true,
                })}
              </p>
            </div>
            <div className="flex items-center gap-2 ml-4">
              {!notification.is_read && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMarkAsRead(notification);
                  }}
                  className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded"
                  title="Mark as read"
                >
                  <CheckIcon className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(notification.id);
                }}
                className="p-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded"
                title="Delete"
              >
                <Trash2Icon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
