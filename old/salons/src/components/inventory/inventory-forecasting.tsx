import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  TrendingUpIcon,
  TrendingDownIcon,
  AlertTriangleIcon,
  PackageIcon,
  CalendarIcon,
} from "@/components/icons";
import { useInventory } from "@/lib/api/hooks/useInventory";
import { InventoryProduct } from "@/lib/api/types";

interface ForecastData {
  product: InventoryProduct;
  dailyUsage: number;
  daysUntilStockout: number;
  reorderDate: string;
  trend: "increasing" | "decreasing" | "stable";
}

export function InventoryForecasting() {
  const { data: products = [], isLoading } = useInventory();

  // Calculate forecast data for each product
  const forecastData: ForecastData[] = products
    .map((product: InventoryProduct) => {
      // Simulate AI forecast calculations
      // In production, this would come from the backend
      const dailyUsage = Math.max(1, Math.floor(product.quantity / 30)); // Estimate based on current stock
      const daysUntilStockout = Math.floor(product.quantity / dailyUsage);
      const reorderDate = new Date();
      reorderDate.setDate(
        reorderDate.getDate() + Math.max(0, daysUntilStockout - 7)
      );

      // Determine trend based on stock level vs reorder level
      let trend: "increasing" | "decreasing" | "stable" = "stable";
      if (product.quantity < product.reorder_level) {
        trend = "decreasing";
      } else if (product.quantity > product.reorder_level * 2) {
        trend = "increasing";
      }

      return {
        product,
        dailyUsage,
        daysUntilStockout,
        reorderDate: reorderDate.toISOString().split("T")[0],
        trend,
      };
    })
    .filter((f) => f.daysUntilStockout < 30) // Only show products that need attention
    .sort((a, b) => a.daysUntilStockout - b.daysUntilStockout);

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-3">
          <Spinner />
          <span className="text-muted-foreground">
            Analyzing inventory trends...
          </span>
        </div>
      </Card>
    );
  }

  if (forecastData.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <PackageIcon
            size={48}
            className="mx-auto text-muted-foreground mb-3"
          />
          <h3 className="font-semibold text-foreground mb-2">
            All Stock Levels Healthy
          </h3>
          <p className="text-sm text-muted-foreground">
            No products require immediate attention based on current usage
            trends
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Alert */}
      <Alert variant="warning">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Inventory Forecast Alert</h3>
          <p className="text-sm">
            {forecastData.length} product{forecastData.length !== 1 ? "s" : ""}{" "}
            may run out within the next 30 days based on current usage patterns
          </p>
        </div>
      </Alert>

      {/* Forecast Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {forecastData.map((forecast) => (
          <Card key={forecast.product.id} className="p-4">
            {/* Product Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="font-semibold text-foreground mb-1">
                  {forecast.product.name}
                </h3>
                <Badge variant="secondary" size="sm">
                  {forecast.product.category}
                </Badge>
              </div>
              {forecast.trend === "decreasing" ? (
                <TrendingDownIcon size={20} className="text-[var(--error)]" />
              ) : forecast.trend === "increasing" ? (
                <TrendingUpIcon size={20} className="text-[var(--success)]" />
              ) : (
                <div className="w-5 h-5" />
              )}
            </div>

            {/* Current Stock */}
            <div className="mb-3 p-3 bg-[var(--muted)]/50 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">
                Current Stock
              </p>
              <p className="text-lg font-bold text-foreground">
                {forecast.product.quantity} {forecast.product.unit}
              </p>
            </div>

            {/* Forecast Metrics */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Daily Usage:</span>
                <span className="font-medium text-foreground">
                  ~{forecast.dailyUsage} {forecast.product.unit}/day
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  Days Until Stockout:
                </span>
                <span
                  className={`font-medium ${
                    forecast.daysUntilStockout < 7
                      ? "text-[var(--error)]"
                      : forecast.daysUntilStockout < 14
                      ? "text-[var(--warning)]"
                      : "text-foreground"
                  }`}
                >
                  {forecast.daysUntilStockout} days
                </span>
              </div>
            </div>

            {/* Reorder Suggestion */}
            <div className="pt-3 border-t border-border">
              <div className="flex items-start gap-2">
                <CalendarIcon
                  size={16}
                  className="text-[var(--primary)] mt-0.5"
                />
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground mb-1">
                    Suggested Reorder Date
                  </p>
                  <p className="text-sm font-medium text-foreground">
                    {new Date(forecast.reorderDate).toLocaleDateString(
                      "en-US",
                      {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      }
                    )}
                  </p>
                </div>
              </div>
            </div>

            {/* Urgency Badge */}
            {forecast.daysUntilStockout < 7 && (
              <div className="mt-3">
                <Badge variant="error" className="w-full justify-center">
                  Urgent: Reorder Now
                </Badge>
              </div>
            )}
            {forecast.daysUntilStockout >= 7 &&
              forecast.daysUntilStockout < 14 && (
                <div className="mt-3">
                  <Badge variant="warning" className="w-full justify-center">
                    Reorder Soon
                  </Badge>
                </div>
              )}
          </Card>
        ))}
      </div>

      {/* Usage Trends Summary */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Usage Trends Summary
        </h3>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="p-4 bg-[var(--error)]/10 border border-[var(--error)]/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDownIcon size={20} className="text-[var(--error)]" />
              <span className="font-semibold text-foreground">
                Critical (
                {forecastData.filter((f) => f.daysUntilStockout < 7).length})
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Products need immediate reordering
            </p>
          </div>

          <div className="p-4 bg-[var(--warning)]/10 border border-[var(--warning)]/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangleIcon size={20} className="text-[var(--warning)]" />
              <span className="font-semibold text-foreground">
                Warning (
                {
                  forecastData.filter(
                    (f) => f.daysUntilStockout >= 7 && f.daysUntilStockout < 14
                  ).length
                }
                )
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Products should be reordered soon
            </p>
          </div>

          <div className="p-4 bg-[var(--info)]/10 border border-[var(--info)]/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <PackageIcon size={20} className="text-[var(--info)]" />
              <span className="font-semibold text-foreground">
                Monitored (
                {
                  forecastData.filter(
                    (f) => f.daysUntilStockout >= 14 && f.daysUntilStockout < 30
                  ).length
                }
                )
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Products to watch in coming weeks
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
