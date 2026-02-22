import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface ReorderSuggestion {
  product_id: string;
  product_name: string;
  current_quantity: number;
  reorder_point: number;
  reorder_quantity: number;
  daily_usage: number;
  days_until_stockout?: number;
  urgency: "critical" | "high" | "medium";
}

export function ForecastingDashboard() {
  const { toast } = useToast();

  const { data: suggestions, isLoading, refetch } = useQuery({
    queryKey: ["reorder-suggestions"],
    queryFn: async () => {
      const res = await apiClient.get("/api/inventory/forecasting/reorder-suggestions");
      return res.data.suggestions || [];
    },
  });

  const handleRefresh = async () => {
    try {
      await apiClient.post("/api/inventory/forecasting/refresh");
      toast("Forecasts refreshed successfully", "success");
      refetch();
    } catch (error) {
      toast("Failed to refresh forecasts", "error");
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "critical":
        return "destructive";
      case "high":
        return "accent";
      case "medium":
        return "secondary";
      default:
        return "secondary";
    }
  };

  const criticalCount = suggestions?.filter((s: ReorderSuggestion) => s.urgency === "critical").length || 0;
  const highCount = suggestions?.filter((s: ReorderSuggestion) => s.urgency === "high").length || 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-[var(--muted-foreground)]">Critical Items</p>
            <p className="text-3xl font-bold text-red-600">{criticalCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-[var(--muted-foreground)]">High Priority</p>
            <p className="text-3xl font-bold text-orange-600">{highCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-[var(--muted-foreground)]">Total Suggestions</p>
            <p className="text-3xl font-bold text-[var(--foreground)]">
              {suggestions?.length || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Refresh Button */}
      <Button onClick={handleRefresh}>Refresh Forecasts</Button>

      {/* Reorder Suggestions */}
      <Card>
        <CardHeader>
          <CardTitle>Reorder Suggestions</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-[var(--muted-foreground)]">Loading suggestions...</p>
          ) : suggestions && suggestions.length > 0 ? (
            <div className="space-y-3">
              {suggestions.map((suggestion: ReorderSuggestion) => (
                <div
                  key={suggestion.product_id}
                  className="p-4 border border-[var(--border)] rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-[var(--foreground)]">
                        {suggestion.product_name}
                      </h4>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Current: {suggestion.current_quantity} units
                      </p>
                    </div>
                    <Badge variant={getUrgencyColor(suggestion.urgency)}>
                      {suggestion.urgency.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div>
                      <p className="text-[var(--muted-foreground)]">Daily Usage</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {suggestion.daily_usage.toFixed(2)} units
                      </p>
                    </div>
                    <div>
                      <p className="text-[var(--muted-foreground)]">Days Until Stockout</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {suggestion.days_until_stockout
                          ? suggestion.days_until_stockout.toFixed(0)
                          : "N/A"}{" "}
                        days
                      </p>
                    </div>
                    <div>
                      <p className="text-[var(--muted-foreground)]">Reorder Point</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {suggestion.reorder_point} units
                      </p>
                    </div>
                    <div>
                      <p className="text-[var(--muted-foreground)]">Reorder Qty</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {suggestion.reorder_quantity} units
                      </p>
                    </div>
                  </div>

                  <Button size="sm" className="mt-3">
                    Create PO
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[var(--muted-foreground)]">
              No reorder suggestions at this time
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
