import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  CalendarIcon,
  UsersIcon,
  DollarIcon,
  AlertTriangleIcon,
  RefreshIcon,
  StarIcon,
  GiftIcon,
  TicketIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";
import { format } from "date-fns";

interface Activity {
  id: string;
  type:
    | "booking"
    | "booking_completed"
    | "cancellation"
    | "payment"
    | "payment_failed"
    | "new_client"
    | "review"
    | "gift_card_purchased"
    | "membership_purchased"
    | "inventory_updated"
    | "staff_added"
    | "waitlist_added"
    | "refund_processed"
    | "promo_created"
    | "loyalty_earned"
    | "loyalty_redeemed"
    | "campaign_created"
    | "expense_added"
    | "service_inquiry"
    | "referral_created";
  source?: string;
  message: string;
  timestamp: string;
  metadata?: Record<string, string | number | boolean>;
}

interface ActivityFeedProps {
  activities: Activity[];
  loading?: boolean;
  autoRefresh?: boolean;
  onRefresh?: () => void;
}

const REFRESH_INTERVAL = 30000; // 30 seconds
const INACTIVITY_TIMEOUT = 60000; // 1 minute

function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = useRef<() => void>(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) {
      return;
    }

    const id = setInterval(() => savedCallback.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}

function useUserActivity() {
  const [isActive, setIsActive] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  useEffect(() => {
    const resetTimer = () => {
      setIsActive(true);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        setIsActive(false);
      }, INACTIVITY_TIMEOUT);
    };

    const events = [
      "mousedown",
      "mousemove",
      "keypress",
      "scroll",
      "touchstart",
    ];
    events.forEach((event) => {
      document.addEventListener(event, resetTimer);
    });

    resetTimer();

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, resetTimer);
      });
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return isActive;
}

export function ActivityFeed({
  activities,
  loading = false,
  autoRefresh = true,
  onRefresh,
}: ActivityFeedProps) {
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const isUserActive = useUserActivity();

  const handleRefresh = () => {
    if (onRefresh && !isRefreshing) {
      setIsRefreshing(true);
      onRefresh();
      setLastUpdated(new Date());
      setIsRefreshing(false);
    }
  };

  // Auto-refresh only when user is active
  useInterval(
    () => {
      if (autoRefresh && isUserActive && !loading) {
        handleRefresh();
      }
    },
    autoRefresh && isUserActive ? REFRESH_INTERVAL : null,
  );

  const getActivityIcon = (type: Activity["type"]) => {
    switch (type) {
      case "booking":
      case "booking_completed":
        return CalendarIcon;
      case "cancellation":
        return AlertTriangleIcon;
      case "payment":
      case "payment_failed":
      case "refund_processed":
        return DollarIcon;
      case "new_client":
      case "staff_added":
        return UsersIcon;
      case "review":
        return StarIcon;
      case "gift_card_purchased":
        return GiftIcon;
      case "membership_purchased":
      case "loyalty_earned":
      case "loyalty_redeemed":
        return TicketIcon;
      case "inventory_updated":
      case "waitlist_added":
      case "promo_created":
      case "campaign_created":
      case "expense_added":
      case "service_inquiry":
      case "referral_created":
        return CalendarIcon;
      default:
        return CalendarIcon;
    }
  };

  const getActivityColor = (type: Activity["type"]) => {
    switch (type) {
      case "booking":
        return "text-[var(--success)]";
      case "booking_completed":
        return "text-[var(--success)]";
      case "cancellation":
        return "text-[var(--error)]";
      case "payment":
        return "text-[var(--primary)]";
      case "payment_failed":
        return "text-[var(--error)]";
      case "refund_processed":
        return "text-[var(--primary)]";
      case "new_client":
        return "text-[var(--info)]";
      case "staff_added":
        return "text-[var(--info)]";
      case "review":
        return "text-yellow-500";
      case "gift_card_purchased":
        return "text-purple-500";
      case "membership_purchased":
        return "text-blue-500";
      case "loyalty_earned":
        return "text-blue-500";
      case "loyalty_redeemed":
        return "text-blue-500";
      case "inventory_updated":
        return "text-orange-500";
      case "waitlist_added":
        return "text-cyan-500";
      case "promo_created":
        return "text-green-500";
      case "campaign_created":
        return "text-indigo-500";
      case "expense_added":
        return "text-red-500";
      case "service_inquiry":
        return "text-teal-500";
      case "referral_created":
        return "text-pink-500";
      default:
        return "text-muted-foreground";
    }
  };

  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-left-4 duration-500"
      role="region"
      aria-label="Recent Activity Feed"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Recent Activity
          </h2>
          <p className="text-xs text-muted-foreground mt-1" aria-live="polite">
            Last updated: {format(lastUpdated, "HH:mm:ss")}
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing || loading}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label={
            isRefreshing || loading
              ? "Refreshing activity feed"
              : "Refresh activity feed"
          }
        >
          <RefreshIcon
            size={16}
            className={cn(
              "transition-transform duration-500",
              (isRefreshing || loading) && "animate-spin",
            )}
            aria-hidden="true"
          />
        </Button>
      </div>

      {loading && activities.length === 0 ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300">
          <CalendarIcon
            size={48}
            className="mx-auto text-muted-foreground mb-2"
          />
          <p className="text-muted-foreground">No recent activity</p>
        </div>
      ) : (
        <div className="space-y-3" role="list" aria-label="Recent activities">
          {activities.map((activity, index) => {
            const Icon = getActivityIcon(activity.type);
            const colorClass = getActivityColor(activity.type);

            return (
              <div
                key={activity.id}
                role="listitem"
                tabIndex={0}
                className="flex items-start gap-3 p-3 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform animate-in fade-in-0 slide-in-from-right-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => {
                  if (
                    activity.metadata?.url &&
                    typeof activity.metadata.url === "string"
                  ) {
                    window.location.href = activity.metadata.url;
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (
                      activity.metadata?.url &&
                      typeof activity.metadata.url === "string"
                    ) {
                      window.location.href = activity.metadata.url;
                    }
                  }
                }}
                aria-label={`${activity.type} activity: ${
                  activity.message
                }, ${format(new Date(activity.timestamp), "MMM dd, HH:mm")}`}
              >
                <div
                  className={cn(
                    "p-2 rounded-lg transition-all duration-300 ease-out",
                    "bg-[var(--muted)]",
                  )}
                  aria-hidden="true"
                >
                  <Icon size={16} className={colorClass} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">{activity.message}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {format(new Date(activity.timestamp), "MMM dd, HH:mm")}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
