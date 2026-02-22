import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import {
  DollarIcon,
  XIcon,
  AlertTriangleIcon,
  CalendarIcon,
  GiftIcon,
  StarIcon,
} from "@/components/icons";

interface QuickStats {
  avg_booking_value?: number;
  cancellation_rate?: number;
  no_show_rate?: number;
  online_booking_percentage?: number;
  gift_card_sales?: number;
  loyalty_points_redeemed?: number;
}

interface QuickStatsWidgetProps {
  stats?: QuickStats | null;
  loading?: boolean;
}

export function QuickStatsWidget({
  stats,
  loading = false,
}: QuickStatsWidgetProps) {
  // Provide safe defaults for all stats
  const safeStats: Required<QuickStats> = {
    avg_booking_value: stats?.avg_booking_value ?? 0,
    cancellation_rate: stats?.cancellation_rate ?? 0,
    no_show_rate: stats?.no_show_rate ?? 0,
    online_booking_percentage: stats?.online_booking_percentage ?? 0,
    gift_card_sales: stats?.gift_card_sales ?? 0,
    loyalty_points_redeemed: stats?.loyalty_points_redeemed ?? 0,
  };

  const statItems = [
    {
      label: "Avg Booking Value",
      value: `₦${safeStats.avg_booking_value.toLocaleString()}`,
      icon: DollarIcon,
      color: "text-[var(--primary)]",
      bgColor: "bg-[var(--primary)]/10",
    },
    {
      label: "Cancellation Rate",
      value: `${safeStats.cancellation_rate.toFixed(1)}%`,
      icon: XIcon,
      color: "text-[var(--error)]",
      bgColor: "bg-[var(--error)]/10",
    },
    {
      label: "No-Show Rate",
      value: `${safeStats.no_show_rate.toFixed(1)}%`,
      icon: AlertTriangleIcon,
      color: "text-[var(--warning)]",
      bgColor: "bg-[var(--warning)]/10",
    },
    {
      label: "Online Bookings",
      value: `${safeStats.online_booking_percentage.toFixed(0)}%`,
      icon: CalendarIcon,
      color: "text-[var(--success)]",
      bgColor: "bg-[var(--success)]/10",
    },
    {
      label: "Gift Card Sales",
      value: `₦${safeStats.gift_card_sales.toLocaleString()}`,
      icon: GiftIcon,
      color: "text-[var(--info)]",
      bgColor: "bg-[var(--info)]/10",
    },
    {
      label: "Loyalty Points Used",
      value: safeStats.loyalty_points_redeemed.toLocaleString(),
      icon: StarIcon,
      color: "text-[var(--warning)]",
      bgColor: "bg-[var(--warning)]/10",
    },
  ];

  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-right-4 duration-500"
      role="region"
      aria-label="Quick Statistics Widget"
    >
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">Quick Stats</h2>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : (
        <div
          className="grid grid-cols-1 sm:grid-cols-2 gap-3"
          role="list"
          aria-label="Quick statistics"
        >
          {statItems.map((item, index) => {
            const Icon = item.icon;

            return (
              <div
                key={item.label}
                role="listitem"
                className="flex items-center gap-3 p-3 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform animate-in fade-in-0 slide-in-from-right-2"
                style={{ animationDelay: `${index * 50}ms` }}
                aria-label={`${item.label}: ${item.value}`}
              >
                <div
                  className={`p-2 ${item.bgColor} rounded-lg transition-all duration-300 ease-out hover:scale-110 transform will-change-transform`}
                  aria-hidden="true"
                >
                  <Icon size={20} className={item.color} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-muted-foreground">{item.label}</p>
                  <p className="text-sm font-semibold text-foreground truncate">
                    {item.value}
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
