import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Spinner } from "@/components/ui/spinner";
import {
  TrendingUpIcon,
  TrendingDownIcon,
  XIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface Campaign {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

interface ComparisonData {
  campaign_id: string;
  campaign_name: string;
  total_recipients: number;
  delivered: number;
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
}

export function CampaignComparison() {
  const { toast } = useToast();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get("/api/campaigns", {
        params: { limit: 100 },
      });
      setCampaigns(response.data || []);
    } catch (error) {
      console.error("Failed to load campaigns:", error);
      toast({
        title: "Error",
        description: "Failed to load campaigns",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCampaignToggle = (campaignId: string) => {
    setSelectedCampaigns((prev) =>
      prev.includes(campaignId)
        ? prev.filter((id) => id !== campaignId)
        : [...prev, campaignId]
    );
  };

  const handleCompare = async () => {
    if (selectedCampaigns.length < 2) {
      toast({
        title: "Error",
        description: "Please select at least 2 campaigns to compare",
        variant: "destructive",
      });
      return;
    }

    try {
      setComparing(true);
      const response = await apiClient.post("/api/campaigns/compare", {
        campaign_ids: selectedCampaigns,
      });
      setComparisonData(response.data || []);
    } catch (error) {
      console.error("Failed to compare campaigns:", error);
      toast({
        title: "Error",
        description: "Failed to compare campaigns",
        variant: "destructive",
      });
    } finally {
      setComparing(false);
    }
  };

  const handleClearSelection = () => {
    setSelectedCampaigns([]);
    setComparisonData([]);
  };

  if (loading) {
    return (
      <Card className="p-12 text-center">
        <Spinner size="lg" />
        <p className="text-muted-foreground mt-4">Loading campaigns...</p>
      </Card>
    );
  }

  if (campaigns.length === 0) {
    return (
      <Card className="p-12 text-center">
        <XIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No campaigns found
        </h3>
        <p className="text-muted-foreground">
          Create campaigns first to compare them
        </p>
      </Card>
    );
  }

  // Prepare chart data
  const chartData = comparisonData.map((campaign) => ({
    name: campaign.campaign_name.substring(0, 15),
    "Delivery Rate": campaign.delivery_rate * 100,
    "Open Rate": campaign.open_rate * 100,
    "Click Rate": campaign.click_rate * 100,
    "Conversion Rate": campaign.conversion_rate * 100,
  }));

  const roiChartData = comparisonData.map((campaign) => ({
    name: campaign.campaign_name.substring(0, 15),
    ROI: campaign.roi,
    Revenue: campaign.revenue_generated / 1000, // Scale down for visibility
  }));

  // Find best and worst performers
  const bestDelivery = comparisonData.reduce((prev, current) =>
    prev.delivery_rate > current.delivery_rate ? prev : current
  );
  const bestROI = comparisonData.reduce((prev, current) =>
    prev.roi > current.roi ? prev : current
  );
  const bestConversion = comparisonData.reduce((prev, current) =>
    prev.conversion_rate > current.conversion_rate ? prev : current
  );

  return (
    <div className="space-y-6">
      {/* Campaign Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Campaigns to Compare</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="flex items-center gap-3">
                <Checkbox
                  id={campaign.id}
                  checked={selectedCampaigns.includes(campaign.id)}
                  onCheckedChange={() => handleCampaignToggle(campaign.id)}
                />
                <label
                  htmlFor={campaign.id}
                  className="flex-1 cursor-pointer text-sm font-medium text-foreground"
                >
                  {campaign.name}
                </label>
                <span className="text-xs text-muted-foreground">
                  {new Date(campaign.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>

          <div className="flex gap-2 mt-6">
            <Button
              onClick={handleCompare}
              disabled={selectedCampaigns.length < 2 || comparing}
            >
              {comparing ? "Comparing..." : "Compare Selected"}
            </Button>
            <Button
              variant="outline"
              onClick={handleClearSelection}
              disabled={selectedCampaigns.length === 0}
            >
              Clear Selection
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {comparisonData.length > 0 && (
        <>
          {/* Performance Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-green-900">
                  Best Delivery Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">
                  {(bestDelivery.delivery_rate * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-green-700 mt-1">
                  {bestDelivery.campaign_name}
                </p>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-blue-900">
                  Best Conversion Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-blue-600">
                  {(bestConversion.conversion_rate * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  {bestConversion.campaign_name}
                </p>
              </CardContent>
            </Card>

            <Card className="border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-purple-900">
                  Best ROI
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-purple-600">
                  {bestROI.roi.toFixed(1)}%
                </p>
                <p className="text-sm text-purple-700 mt-1">
                  {bestROI.campaign_name}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Engagement Rates Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Engagement Rates Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Delivery Rate" fill="#10b981" />
                  <Bar dataKey="Open Rate" fill="#3b82f6" />
                  <Bar dataKey="Click Rate" fill="#8b5cf6" />
                  <Bar dataKey="Conversion Rate" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* ROI and Revenue Chart */}
          <Card>
            <CardHeader>
              <CardTitle>ROI & Revenue Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={roiChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="ROI" fill="#10b981" />
                  <Bar dataKey="Revenue" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Detailed Comparison Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-3 font-semibold text-foreground">
                        Campaign
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        Recipients
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        Delivered
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        Opened
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        Conversions
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        Revenue
                      </th>
                      <th className="text-right py-2 px-3 font-semibold text-foreground">
                        ROI
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData.map((campaign) => (
                      <tr key={campaign.campaign_id} className="border-b hover:bg-muted/50">
                        <td className="py-3 px-3 text-foreground font-medium">
                          {campaign.campaign_name}
                        </td>
                        <td className="text-right py-3 px-3 text-muted-foreground">
                          {campaign.total_recipients}
                        </td>
                        <td className="text-right py-3 px-3 text-muted-foreground">
                          {campaign.delivered} (
                          {(campaign.delivery_rate * 100).toFixed(1)}%)
                        </td>
                        <td className="text-right py-3 px-3 text-muted-foreground">
                          {campaign.opened} (
                          {(campaign.open_rate * 100).toFixed(1)}%)
                        </td>
                        <td className="text-right py-3 px-3 text-muted-foreground">
                          {campaign.conversions} (
                          {(campaign.conversion_rate * 100).toFixed(1)}%)
                        </td>
                        <td className="text-right py-3 px-3 text-muted-foreground">
                          ₦{campaign.revenue_generated.toLocaleString()}
                        </td>
                        <td className="text-right py-3 px-3">
                          <div className="flex items-center justify-end gap-1">
                            {campaign.roi >= 0 ? (
                              <TrendingUpIcon size={16} className="text-green-600" />
                            ) : (
                              <TrendingDownIcon size={16} className="text-red-600" />
                            )}
                            <span
                              className={`font-semibold ${
                                campaign.roi >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }`}
                            >
                              {campaign.roi.toFixed(1)}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
