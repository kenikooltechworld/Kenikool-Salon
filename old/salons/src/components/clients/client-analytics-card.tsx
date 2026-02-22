import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarIcon,
  CalendarIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
  UserIcon,
} from "@/components/icons";
import { useGetClientAnalytics } from "@/lib/api/hooks/useClients";

interface ClientAnalyticsCardProps {
  clientId: string;
}

export function ClientAnalyticsCard({ clientId }: ClientAnalyticsCardProps) {
  const { data: analytics, isLoading, error } = useGetClientAnalytics(clientId);

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (error || !analytics) {
    return (
      <Card className="p-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading analytics</h3>
            <p className="text-sm">
              {error?.message || "Analytics not available"}
            </p>
          </div>
        </Alert>
      </Card>
    );
  }

  const getChurnRiskColor = (score: number) => {
    if (score >= 0.7) return "text-red-600 dark:text-red-400";
    if (score >= 0.4) return "text-yellow-600 dark:text-yellow-400";
    return "text-green-600 dark:text-green-400";
  };

  const getChurnRiskLabel = (score: number) => {
    if (score >= 0.7) return "High Risk";
    if (score >= 0.4) return "Medium Risk";
    return "Low Risk";
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Client Analytics
        </h2>
        {analytics.is_at_risk && (
          <span className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full">
            At Risk
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Lifetime Value */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <DollarIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">Lifetime Value</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            ₦{analytics.lifetime_value?.toLocaleString() || "0"}
          </p>
        </div>

        {/* Average Spend */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <DollarIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">Avg Spend per Visit</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            ₦{analytics.average_transaction_value?.toLocaleString() || "0"}
          </p>
        </div>

        {/* Visit Frequency */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <CalendarIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">Visit Frequency</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {analytics.average_days_between_visits
              ? `Every ${Math.round(
                  analytics.average_days_between_visits,
                )} days`
              : "N/A"}
          </p>
        </div>

        {/* Predicted Next Visit */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUpIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">
              Predicted Next Visit
            </p>
          </div>
          <p className="text-lg font-bold text-foreground">
            {analytics.predicted_next_visit
              ? new Date(analytics.predicted_next_visit).toLocaleDateString(
                  "en-US",
                  {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  },
                )
              : "Unknown"}
          </p>
        </div>

        {/* Attendance Rate */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <UserIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">Attendance Rate</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {analytics.attendance_rate
              ? `${(analytics.attendance_rate * 100).toFixed(0)}%`
              : "N/A"}
          </p>
          {analytics.no_show_count > 0 && (
            <p className="text-xs text-muted-foreground mt-1">
              {analytics.no_show_count} no-show
              {analytics.no_show_count !== 1 ? "s" : ""}
            </p>
          )}
        </div>

        {/* Churn Risk */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangleIcon size={20} className="text-primary" />
            <p className="text-sm text-muted-foreground">Churn Risk</p>
          </div>
          <p
            className={`text-2xl font-bold ${getChurnRiskColor(
              analytics.churn_risk_score || 0,
            )}`}
          >
            {getChurnRiskLabel(analytics.churn_risk_score || 0)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {analytics.days_since_last_visit} days since last visit
          </p>
        </div>
      </div>

      {/* Favorite Services */}
      {analytics.favorite_services &&
        analytics.favorite_services.length > 0 && (
          <div className="mt-6 pt-6 border-t border-border">
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Favorite Services
            </h3>
            <div className="flex flex-wrap gap-2">
              {analytics.favorite_services.map(
                (service: string, index: number) => (
                  <span
                    key={index}
                    className="px-3 py-1 text-sm bg-primary/10 text-primary rounded-full"
                  >
                    {service}
                  </span>
                ),
              )}
            </div>
          </div>
        )}

      {/* Favorite Stylists */}
      {analytics.favorite_stylists &&
        analytics.favorite_stylists.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Favorite Stylists
            </h3>
            <div className="flex flex-wrap gap-2">
              {analytics.favorite_stylists.map(
                (stylist: string, index: number) => (
                  <span
                    key={index}
                    className="px-3 py-1 text-sm bg-secondary/10 text-secondary rounded-full"
                  >
                    {stylist}
                  </span>
                ),
              )}
            </div>
          </div>
        )}
    </Card>
  );
}
