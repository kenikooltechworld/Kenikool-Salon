import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import {
  MailIcon,
  UsersIcon,
  CheckCircleIcon,
  XIcon,
  DollarSignIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface CampaignAnalyticsEnhancedProps {
  campaignId: string;
}

interface AnalyticsData {
  campaign_id: string;
  campaign_name: string;
  total_recipients: number;
  delivered: number;
  failed: number;
  delivery_rate: number;
  opened: number;
  open_rate: number;
  clicked: number;
  click_rate: number;
  conversions: number;
  conversion_rate: number;
  revenue_generated: number;
  roi: number;
  total_cost: number;
  cost_per_conversion: number;
  channel_stats: Array<{
    channel: string;
    sent: number;
    delivered: number;
    opened: number;
    clicked: number;
    cost: number;
  }>;
  daily_stats: Array<{
    date: string;
    delivered: number;
    opened: number;
    clicked: number;
    conversions: number;
  }>;
  cost_breakdown: Record<string, number>;
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export function CampaignAnalyticsEnhanced({
  campaignId,
}: CampaignAnalyticsEnhancedProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, [campaignId]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(
        `/api/campaigns/${campaignId}/analytics-detailed`
      );
      setAnalytics(response.data);
    } catch (err) {
      const errorMsg = "Failed to load analytics";
      setError(errorMsg);
      console.error(errorMsg, err);
      toast({
        title: "Error",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-12 text-center">
        <Spinner size="lg" />
        <p className="text-muted-foreground mt-4">Loading analytics...</p>
      </Card>
    );
  }

  if (error || !analytics) {
    return (
      <Card className="p-12 text-center">
        <XIcon size={48} className="mx-auto text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Failed to load analytics
        </h3>
        <p className="text-muted-foreground">{error}</p>
      </Card>
    );
  }

  const deliveryRate = analytics.delivery_rate * 100;
  const openRate = analytics.open_rate * 100;
  const clickRate = analytics.click_rate * 100;
  const conversionRate = analytics.conversion_rate * 100;

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CheckCircleIcon size={16} />
              Delivery Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">
              {deliveryRate.toFixed(1)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {analytics.delivered} of {analytics.total_recipients}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <MailIcon size={16} />
              Open Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">
              {openRate.toFixed(1)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {analytics.opened} opens
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUpIcon size={16} />
              Click Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-600">
              {clickRate.toFixed(1)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {analytics.clicked} clicks
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSignIcon size={16} />
              ROI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p
              className={`text-3xl font-bold ${
                analytics.roi >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {analytics.roi.toFixed(1)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Revenue: ₦{analytics.revenue_generated.toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Time Series Chart */}
      {analytics.daily_stats && analytics.daily_stats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Performance Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="delivered"
                  stroke="#10b981"
                  name="Delivered"
                />
                <Line
                  type="monotone"
                  dataKey="opened"
                  stroke="#3b82f6"
                  name="Opened"
                />
                <Line
                  type="monotone"
                  dataKey="clicked"
                  stroke="#8b5cf6"
                  name="Clicked"
                />
                <Line
                  type="monotone"
                  dataKey="conversions"
                  stroke="#f59e0b"
                  name="Conversions"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Channel Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Channel Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.channel_stats.map((channel) => (
                <div key={channel.channel} className="border-b pb-4 last:border-b-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-foreground capitalize">
                      {channel.channel}
                    </h4>
                    <span className="text-sm text-muted-foreground">
                      ₦{channel.cost.toLocaleString()}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Sent</p>
                      <p className="font-semibold text-foreground">
                        {channel.sent}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Delivered</p>
                      <p className="font-semibold text-foreground">
                        {channel.delivered}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Opened</p>
                      <p className="font-semibold text-foreground">
                        {channel.opened}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Clicked</p>
                      <p className="font-semibold text-foreground">
                        {channel.clicked}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown Pie Chart */}
        {Object.keys(analytics.cost_breakdown).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown by Channel</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={Object.entries(analytics.cost_breakdown).map(
                      ([channel, cost]) => ({
                        name: channel,
                        value: cost,
                      })
                    )}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) =>
                      `${name}: ₦${value.toLocaleString()}`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.keys(analytics.cost_breakdown).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => `₦${value.toLocaleString()}`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Financial Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Financial Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Cost</p>
              <p className="text-2xl font-bold text-foreground">
                ₦{analytics.total_cost.toLocaleString()}
              </p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">
                Cost per Conversion
              </p>
              <p className="text-2xl font-bold text-foreground">
                ₦{analytics.cost_per_conversion.toLocaleString()}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">
                Revenue Generated
              </p>
              <p className="text-2xl font-bold text-green-600">
                ₦{analytics.revenue_generated.toLocaleString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Conversion Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Conversion Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-foreground">
                  Conversion Rate
                </span>
                <span className="text-sm font-semibold text-foreground">
                  {conversionRate.toFixed(2)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-500"
                  style={{ width: `${Math.min(conversionRate, 100)}%` }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-xs text-muted-foreground mb-1">
                  Total Conversions
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {analytics.conversions}
                </p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-xs text-muted-foreground mb-1">
                  Failed Deliveries
                </p>
                <p className="text-2xl font-bold text-red-600">
                  {analytics.failed}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
