import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  BellIcon,
  CheckIcon,
  AlertTriangleIcon,
  DollarIcon,
  CalendarIcon,
  StarIcon,
  InfoIcon,
  TrashIcon,
} from "@/components/icons";
import {
  useNotifications,
  useUpdateNotification,
  useMarkAllNotificationsRead,
  useDeleteNotification,
} from "@/lib/api/hooks/useNotifications";
import { formatDistanceToNow } from "date-fns";
import type { Notification, NotificationType } from "@/lib/api/types";

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const { data, isLoading, error } = useNotifications({
    is_read: filter === "unread" ? false : undefined,
    limit: 50,
  });

  const updateNotification = useUpdateNotification();
  const markAllRead = useMarkAllNotificationsRead();
  const deleteNotification = useDeleteNotification();

  const notifications = data?.notifications || [];
  const unreadCount = data?.unread_count || 0;

  const getNotificationIcon = (type: NotificationType) => {
    switch (type) {
      case "booking":
        return <CalendarIcon size={24} className="text-[var(--primary)]" />;
      case "payment":
        return <DollarIcon size={24} className="text-[var(--success)]" />;
      case "review":
        return <StarIcon size={24} className="text-[var(--warning)]" />;
      case "inventory":
      case "system":
        return <AlertTriangleIcon size={24} className="text-[var(--error)]" />;
      default:
        return <InfoIcon size={24} className="text-muted-foreground" />;
    }
  };

  const getNotificationTypeLabel = (type: NotificationType) => {
    switch (type) {
      case "booking":
        return "Booking";
      case "payment":
        return "Payment";
      case "review":
        return "Review";
      case "inventory":
        return "Inventory";
      case "system":
        return "System";
      default:
        return "General";
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      updateNotification.mutate({
        id: notification.id,
        is_read: true,
      });
    }

    if (notification.link) {
      navigate(notification.link);
    }
  };

  const handleMarkAsRead = (notificationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    updateNotification.mutate({
      id: notificationId,
      is_read: true,
    });
  };

  const handleMarkAsUnread = (notificationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    updateNotification.mutate({
      id: notificationId,
      is_read: false,
    });
  };

  const handleDelete = (notificationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this notification?")) {
      deleteNotification.mutate(notificationId);
    }
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading notifications</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Notifications</h1>
          <p className="text-muted-foreground">
            Stay updated with your salon activities
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
          >
            {markAllRead.isPending ? (
              <>
                <Spinner size="sm" />
                Marking...
              </>
            ) : (
              <>
                <CheckIcon size={20} />
                Mark all as read
              </>
            )}
          </Button>
        )}
      </div>

      {/* Filter Tabs */}
      <Card className="p-2">
        <div className="flex gap-2">
          <Button
            variant={filter === "all" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setFilter("all")}
          >
            All
            {data?.total ? (
              <Badge className="ml-2 bg-muted text-muted-foreground">
                {data.total}
              </Badge>
            ) : null}
          </Button>
          <Button
            variant={filter === "unread" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setFilter("unread")}
          >
            Unread
            {unreadCount > 0 ? (
              <Badge className="ml-2 bg-[var(--error)] text-white">
                {unreadCount}
              </Badge>
            ) : null}
          </Button>
        </div>
      </Card>

      {/* Notifications List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : notifications.length > 0 ? (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <Card
              key={notification.id}
              className={`p-6 cursor-pointer hover:shadow-md transition-all ${
                !notification.is_read
                  ? "border-l-4 border-l-[var(--primary)] bg-[var(--primary)]/5"
                  : ""
              }`}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  {getNotificationIcon(notification.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-foreground">
                          {notification.title}
                        </h3>
                        <Badge
                          className={
                            notification.type === "booking"
                              ? "bg-[var(--primary)]/10 text-[var(--primary)]"
                              : notification.type === "payment"
                                ? "bg-[var(--success)]/10 text-[var(--success)]"
                                : notification.type === "review"
                                  ? "bg-[var(--warning)]/10 text-[var(--warning)]"
                                  : notification.type === "inventory" ||
                                      notification.type === "system"
                                    ? "bg-[var(--error)]/10 text-[var(--error)]"
                                    : "bg-muted text-muted-foreground"
                          }
                        >
                          {getNotificationTypeLabel(notification.type)}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground">
                        {notification.message}
                      </p>
                      <p className="text-sm text-muted-foreground mt-2">
                        {formatDistanceToNow(
                          new Date(notification.created_at),
                          {
                            addSuffix: true,
                          },
                        )}
                      </p>
                    </div>

                    {!notification.is_read && (
                      <div className="w-3 h-3 rounded-full bg-[var(--primary)] flex-shrink-0 mt-1" />
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-4">
                    {!notification.is_read ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => handleMarkAsRead(notification.id, e)}
                      >
                        <CheckIcon size={16} />
                        Mark as read
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => handleMarkAsUnread(notification.id, e)}
                      >
                        Mark as unread
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => handleDelete(notification.id, e)}
                    >
                      <TrashIcon size={16} />
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12">
          <div className="text-center">
            <BellIcon
              size={64}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No notifications
            </h3>
            <p className="text-muted-foreground">
              {filter === "unread"
                ? "You're all caught up! No unread notifications."
                : "You don't have any notifications yet."}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
