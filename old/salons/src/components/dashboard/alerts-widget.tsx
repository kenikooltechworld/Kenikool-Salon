import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  AlertTriangleIcon,
  XIcon,
  PackageIcon,
  CalendarIcon,
  DollarIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface Alert {
  id: string;
  type:
    | "inventory"
    | "pending_booking"
    | "schedule_conflict"
    | "payment_failure";
  severity: "low" | "medium" | "high";
  message: string;
  action_url?: string;
}

interface AlertsWidgetProps {
  alerts: Alert[];
  loading?: boolean;
  onDismiss?: (alertId: string) => void;
}

export function AlertsWidget({
  alerts,
  loading = false,
  onDismiss,
}: AlertsWidgetProps) {
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(
    new Set()
  );

  const handleDismiss = (alertId: string) => {
    setDismissedAlerts((prev) => new Set(prev).add(alertId));
    onDismiss?.(alertId);
  };

  const visibleAlerts = alerts.filter(
    (alert) => !dismissedAlerts.has(alert.id)
  );

  const getAlertIcon = (type: Alert["type"]) => {
    switch (type) {
      case "inventory":
        return PackageIcon;
      case "pending_booking":
        return CalendarIcon;
      case "payment_failure":
        return DollarIcon;
      default:
        return AlertTriangleIcon;
    }
  };

  const getSeverityColor = (severity: Alert["severity"]) => {
    switch (severity) {
      case "high":
        return "text-[var(--error)]";
      case "medium":
        return "text-[var(--warning)]";
      case "low":
        return "text-[var(--info)]";
      default:
        return "text-muted-foreground";
    }
  };

  const getSeverityBadge = (severity: Alert["severity"]) => {
    switch (severity) {
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "default";
      default:
        return "default";
    }
  };

  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-right-4 duration-500"
      role="region"
      aria-label="System Alerts"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Alerts</h2>
          {visibleAlerts.length > 0 && (
            <Badge
              variant="error"
              aria-label={`${visibleAlerts.length} active alerts`}
            >
              {visibleAlerts.length}
            </Badge>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : visibleAlerts.length === 0 ? (
        <div className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300">
          <AlertTriangleIcon
            size={48}
            className="mx-auto text-muted-foreground mb-2"
          />
          <p className="text-muted-foreground">No alerts at this time</p>
          <p className="text-sm text-muted-foreground mt-1">
            You're all caught up!
          </p>
        </div>
      ) : (
        <div className="space-y-3" role="list" aria-label="Active alerts">
          {visibleAlerts.map((alert, index) => {
            const Icon = getAlertIcon(alert.type);
            const colorClass = getSeverityColor(alert.severity);

            return (
              <div
                key={alert.id}
                role="listitem"
                className="flex items-start gap-3 p-3 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform animate-in fade-in-0 slide-in-from-right-2"
                style={{ animationDelay: `${index * 50}ms` }}
                aria-label={`${alert.severity} severity ${alert.type} alert: ${alert.message}`}
              >
                <div
                  className={cn(
                    "p-2 rounded-lg transition-all duration-300 ease-out",
                    "bg-[var(--muted)]"
                  )}
                  aria-hidden="true"
                >
                  <Icon size={16} className={colorClass} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <p className="text-sm text-foreground flex-1">
                      {alert.message}
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDismiss(alert.id)}
                      className="h-6 w-6 p-0 hover:bg-[var(--error)]/10 transition-all duration-200"
                      aria-label={`Dismiss ${alert.type} alert`}
                    >
                      <XIcon size={14} aria-hidden="true" />
                      <span className="sr-only">Dismiss alert</span>
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={getSeverityBadge(alert.severity) as any}
                      aria-label={`${alert.severity} severity`}
                    >
                      {alert.severity}
                    </Badge>
                    {alert.action_url && (
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() =>
                          (window.location.href = alert.action_url!)
                        }
                        className="h-auto p-0 text-xs"
                        aria-label={`Take action on ${alert.type} alert`}
                      >
                        Take Action →
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
