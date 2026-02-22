import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  ScissorsIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface TopService {
  id: string;
  name: string;
  booking_count: number;
  revenue: number;
  trend: number;
}

interface TopServicesWidgetProps {
  services: TopService[];
  loading?: boolean;
  onServiceClick?: (serviceId: string) => void;
}

export function TopServicesWidget({
  services,
  loading = false,
  onServiceClick,
}: TopServicesWidgetProps) {
  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-left-4 duration-500"
      role="region"
      aria-label="Top performing services"
    >
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-lg font-semibold text-foreground"
          id="top-services-heading"
        >
          Top Services
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (window.location.href = "/dashboard/services")}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label="View all services"
        >
          View All
        </Button>
      </div>

      {loading ? (
        <div
          className="flex justify-center py-8"
          role="status"
          aria-live="polite"
        >
          <Spinner />
          <span className="sr-only">Loading top services...</span>
        </div>
      ) : services.length === 0 ? (
        <div
          className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300"
          role="status"
        >
          <ScissorsIcon
            size={48}
            className="mx-auto text-muted-foreground mb-2"
            aria-hidden="true"
          />
          <p className="text-muted-foreground">No services data available</p>
        </div>
      ) : (
        <div
          className="space-y-3"
          role="list"
          aria-labelledby="top-services-heading"
        >
          {services.map((service, index) => {
            const isPositiveTrend = service.trend >= 0;

            return (
              <div
                key={service.id}
                role="listitem"
                tabIndex={0}
                className="flex items-center gap-3 p-3 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform cursor-pointer animate-in fade-in-0 slide-in-from-right-2 focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => onServiceClick?.(service.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onServiceClick?.(service.id);
                  }
                }}
                aria-label={`${service.name}: ${
                  service.booking_count
                } bookings, ${service.revenue.toLocaleString()} Naira revenue, ${Math.abs(
                  service.trend
                ).toFixed(1)}% ${isPositiveTrend ? "increase" : "decrease"}`}
              >
                <div
                  className="p-2 bg-[var(--primary)]/10 rounded-lg transition-all duration-300 ease-out hover:bg-[var(--primary)]/20 hover:scale-110 transform will-change-transform"
                  aria-hidden="true"
                >
                  <ScissorsIcon size={20} className="text-[var(--primary)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground truncate">
                    {service.name}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>{service.booking_count} bookings</span>
                    <span aria-hidden="true">•</span>
                    <span>₦{service.revenue.toLocaleString()}</span>
                  </div>
                </div>
                {service.trend !== 0 && (
                  <div className="flex items-center gap-1">
                    {isPositiveTrend ? (
                      <TrendingUpIcon
                        size={16}
                        className="text-[var(--success)]"
                      />
                    ) : (
                      <TrendingDownIcon
                        size={16}
                        className="text-[var(--error)]"
                      />
                    )}
                    <span
                      className={cn(
                        "text-sm font-medium",
                        isPositiveTrend
                          ? "text-[var(--success)]"
                          : "text-[var(--error)]"
                      )}
                    >
                      {isPositiveTrend ? "+" : ""}
                      {service.trend.toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
