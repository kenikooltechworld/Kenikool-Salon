import { memo } from "react";
import { useUnreadNotificationCount } from "@/hooks/useNotifications";
import { BellIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface NotificationBadgeProps {
  onClick?: () => void;
  className?: string;
}

const NotificationBadge = memo(function NotificationBadge({
  onClick,
  className,
}: NotificationBadgeProps) {
  const { data: unreadCount = 0, isLoading } = useUnreadNotificationCount();

  return (
    <button
      onClick={onClick}
      className={cn("relative p-2 cursor-pointer transition-colors", className)}
      style={{
        color: "var(--muted-foreground)",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.color = "var(--foreground)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.color = "var(--muted-foreground)";
      }}
      aria-label="Notifications"
    >
      <BellIcon className="w-6 h-6" />
      {unreadCount > 0 && !isLoading && (
        <span
          className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none transform translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{
            backgroundColor: "var(--destructive)",
            color: "var(--destructive-foreground)",
          }}
        >
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </button>
  );
});

export default NotificationBadge;
