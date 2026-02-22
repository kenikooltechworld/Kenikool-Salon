import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { ClockIcon, AlertTriangleIcon } from "@/components/icons";

interface WaitlistService {
  service_name: string;
  count: number;
}

interface WaitlistSummaryWidgetProps {
  totalCount: number;
  byService: WaitlistService[];
  urgentCount: number;
  loading?: boolean;
}

export function WaitlistSummaryWidget({
  totalCount,
  byService,
  urgentCount,
  loading = false,
}: WaitlistSummaryWidgetProps) {
  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-left-4 duration-500"
      role="region"
      aria-label="Waitlist Summary Widget"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Waitlist</h2>
          {totalCount > 0 && (
            <Badge
              variant="warning"
              aria-label={`${totalCount} people on waitlist`}
            >
              {totalCount}
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (window.location.href = "/dashboard/waitlist")}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label="Manage waitlist"
        >
          Manage
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : totalCount === 0 ? (
        <div className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300">
          <ClockIcon size={48} className="mx-auto text-muted-foreground mb-2" />
          <p className="text-muted-foreground">No waitlist entries</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Urgent Count */}
          {urgentCount > 0 && (
            <div
              className="p-3 bg-[var(--error)]/10 border border-[var(--error)]/20 rounded-lg"
              role="alert"
              aria-live="polite"
            >
              <div className="flex items-center gap-2">
                <AlertTriangleIcon
                  size={16}
                  className="text-[var(--error)]"
                  aria-hidden="true"
                />
                <p className="text-sm font-medium text-[var(--error)]">
                  {urgentCount} urgent {urgentCount === 1 ? "entry" : "entries"}{" "}
                  (7+ days)
                </p>
              </div>
            </div>
          )}

          {/* By Service */}
          <div
            className="space-y-2"
            role="group"
            aria-label="Waitlist by service"
          >
            <p className="text-sm font-medium text-foreground">By Service</p>
            <div role="list">
              {byService.slice(0, 5).map((item, index) => (
                <div
                  key={item.service_name}
                  role="listitem"
                  className="flex items-center justify-between p-2 bg-[var(--muted)]/50 rounded hover:bg-[var(--muted)] transition-all duration-200 animate-in fade-in-0 slide-in-from-right-2"
                  style={{ animationDelay: `${index * 50}ms` }}
                  aria-label={`${item.service_name}: ${item.count} waiting`}
                >
                  <span className="text-sm text-foreground">
                    {item.service_name}
                  </span>
                  <Badge
                    variant="default"
                    aria-label={`${item.count} people waiting`}
                  >
                    {item.count}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Total Summary */}
          <div className="pt-3 border-t border-[var(--muted)]">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">
                Total Waiting
              </span>
              <span className="text-lg font-bold text-foreground">
                {totalCount}
              </span>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
