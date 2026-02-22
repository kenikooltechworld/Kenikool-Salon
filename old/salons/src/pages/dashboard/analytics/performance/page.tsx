import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  TrophyIcon,
  ChartIcon,
  UsersIcon,
  DollarIcon,
  StarIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { Badge } from "@/components/ui/badge";
import { FeatureGate } from "@/components/subscriptions/feature-gate";
import { apiClient } from "@/lib/api/client";

export default function PerformanceDashboardPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [staffPerformance, setStaffPerformance] = useState<any>(null);
  const [serviceEfficiency, setServiceEfficiency] = useState<any[]>([]);
  const [clientRetention, setClientRetention] = useState<any>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      // Fetch staff performance
      const staffRes = await apiClient.get(`/api/analytics/staff-performance`, {
        params,
      });
      setStaffPerformance(staffRes.data);

      // Fetch service efficiency
      const serviceRes = await apiClient.get(
        `/api/analytics/service-efficiency`,
        { params },
      );
      setServiceEfficiency(serviceRes.data);

      // Fetch client retention
      const retentionRes = await apiClient.get(
        `/api/analytics/client-retention`,
        { params },
      );
      setClientRetention(retentionRes.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRankBadge = (index: number) => {
    if (index === 0) return <Badge className="bg-yellow-500">🥇 1st</Badge>;
    if (index === 1) return <Badge className="bg-gray-400">🥈 2nd</Badge>;
    if (index === 2) return <Badge className="bg-orange-600">🥉 3rd</Badge>;
    return <Badge variant="secondary">#{index + 1}</Badge>;
  };

  return (
    <FeatureGate feature="Advanced Analytics" requiredPlan="professional">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Staff Performance Analytics
          </h1>
          <p className="text-muted-foreground">
            Track staff metrics, service efficiency, and client retention
          </p>
        </div>

        {/* Date Range Filter */}
        <Card className="p-4">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <Button onClick={fetchAnalytics} disabled={loading}>
              {loading ? "Loading..." : "Load Analytics"}
            </Button>
          </div>
        </Card>

        {error && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Error</h3>
              <p className="text-sm">{error}</p>
            </div>
          </Alert>
        )}

        {loading && (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        )}

        {!loading && staffPerformance && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <DollarIcon size={24} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Total Revenue
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        ₦{staffPerformance.total_revenue.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <StarIcon size={24} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Average Rating
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        {staffPerformance.average_rating.toFixed(1)} ⭐
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {clientRetention && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-primary/10 rounded-lg">
                        <UsersIcon size={24} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Client Retention
                        </p>
                        <p className="text-2xl font-bold text-foreground">
                          {clientRetention.retention_rate.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Staff Leaderboard */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <TrophyIcon size={24} className="text-primary" />
                  <CardTitle>Staff Leaderboard</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {staffPerformance.metrics.map((staff: any, index: number) => (
                    <div
                      key={staff.staff_id}
                      className="flex items-center justify-between p-4 bg-muted/50 rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        {getRankBadge(index)}
                        <div>
                          <p className="font-semibold text-foreground">
                            {staff.staff_name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {staff.completed_bookings} bookings •{" "}
                            {staff.average_rating.toFixed(1)} ⭐
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-foreground">
                          ₦{staff.total_revenue.toLocaleString()}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {staff.client_retention_rate.toFixed(1)}% retention
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Service Efficiency */}
            {serviceEfficiency.length > 0 && (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <ChartIcon size={24} className="text-primary" />
                    <CardTitle>Service Efficiency</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {serviceEfficiency.map((service: any) => (
                      <div
                        key={service.service_id}
                        className="flex items-center justify-between p-4 bg-muted/50 rounded-lg"
                      >
                        <div>
                          <p className="font-semibold text-foreground">
                            {service.service_name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {service.total_bookings} bookings •{" "}
                            {service.average_duration.toFixed(0)} min avg
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-foreground">
                            ₦{service.average_revenue.toLocaleString()}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {service.popularity_score.toFixed(2)} bookings/day
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Client Retention Details */}
            {clientRetention && (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <UsersIcon size={24} className="text-primary" />
                    <CardTitle>Client Retention Metrics</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Total Clients
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        {clientRetention.total_clients}
                      </p>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Returning
                      </p>
                      <p className="text-2xl font-bold text-green-600">
                        {clientRetention.returning_clients}
                      </p>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        New Clients
                      </p>
                      <p className="text-2xl font-bold text-blue-600">
                        {clientRetention.new_clients}
                      </p>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Churn Rate
                      </p>
                      <p className="text-2xl font-bold text-red-600">
                        {clientRetention.churn_rate.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {!loading && !staffPerformance && (
          <Card className="p-12">
            <div className="text-center">
              <ChartIcon
                size={48}
                className="mx-auto text-muted-foreground mb-4"
              />
              <h3 className="text-lg font-semibold text-foreground mb-2">
                No Data Yet
              </h3>
              <p className="text-muted-foreground mb-4">
                Select a date range and click "Load Analytics" to view
                performance metrics
              </p>
            </div>
          </Card>
        )}
      </div>
    </FeatureGate>
  );
}
