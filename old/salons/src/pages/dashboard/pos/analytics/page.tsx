import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useGetPOSAnalytics } from "@/lib/api/hooks/usePOS";
import { formatCurrency } from "@/lib/utils/currency";
import {
  BarChart3Icon,
  TrendingUpIcon,
  DollarSignIcon,
  ShoppingCartIcon,
  ClockIcon,
  UsersIcon,
  CreditCardIcon,
  PackageIcon,
} from "@/components/icons";

export default function POSAnalyticsPage() {
  const today = new Date().toISOString().split("T")[0];
  const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split("T")[0];

  const [dateFrom, setDateFrom] = useState(lastWeek);
  const [dateTo, setDateTo] = useState(today);
  const [interval, setInterval] = useState<"hour" | "day" | "week" | "month">(
    "day"
  );

  const { data: analytics, isLoading } = useGetPOSAnalytics(
    dateFrom,
    dateTo,
    interval
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">POS Analytics</h1>
          <p className="text-muted-foreground">
            Sales performance and insights
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date-from">From Date</Label>
              <Input
                id="date-from"
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date-to">To Date</Label>
              <Input
                id="date-to"
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="interval">Interval</Label>
              <Select
                value={interval}
                onValueChange={(value: any) => setInterval(value)}
              >
                <SelectTrigger id="interval">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hour">Hourly</SelectItem>
                  <SelectItem value="day">Daily</SelectItem>
                  <SelectItem value="week">Weekly</SelectItem>
                  <SelectItem value="month">Monthly</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button
                onClick={() => {
                  setDateFrom(lastWeek);
                  setDateTo(today);
                }}
                variant="outline"
                className="w-full"
              >
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      ) : analytics ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Sales
                </CardTitle>
                <DollarSignIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(analytics.total_sales)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Transactions
                </CardTitle>
                <ShoppingCartIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics.total_transactions}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Avg Transaction
                </CardTitle>
                <TrendingUpIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(analytics.average_transaction)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Peak Hour</CardTitle>
                <ClockIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics.peak_hours && analytics.peak_hours.length > 0
                    ? `${analytics.peak_hours[0].hour}:00`
                    : "N/A"}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Best Selling Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3Icon className="h-5 w-5" />
                Best Selling Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analytics.best_selling_items &&
              analytics.best_selling_items.length > 0 ? (
                <div className="space-y-3">
                  {analytics.best_selling_items.map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-muted rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium">{item.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {item.quantity} sold
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">
                          {formatCurrency(item.revenue)}
                        </p>
                        <p className="text-xs text-muted-foreground">revenue</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No sales data available
                </p>
              )}
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Peak Hours */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ClockIcon className="h-5 w-5" />
                  Peak Hours
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.peak_hours && analytics.peak_hours.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.peak_hours.map((hour, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-muted rounded"
                      >
                        <span className="font-medium">
                          {hour.hour}:00 - {hour.hour + 1}:00
                        </span>
                        <div className="text-right">
                          <p className="text-sm font-medium">
                            {hour.transactions} transactions
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatCurrency(hour.revenue)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No data available
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Payment Methods */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCardIcon className="h-5 w-5" />
                  Payment Methods
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.payment_method_breakdown &&
                Object.keys(analytics.payment_method_breakdown).length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(analytics.payment_method_breakdown).map(
                      ([method, amount]) => (
                        <div
                          key={method}
                          className="flex items-center justify-between p-2 bg-muted rounded"
                        >
                          <span className="font-medium capitalize">
                            {method}
                          </span>
                          <span className="font-bold">
                            {formatCurrency(amount as number)}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No payment data available
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Category Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PackageIcon className="h-5 w-5" />
                  Category Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.category_performance &&
                analytics.category_performance.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.category_performance.map((category, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-muted rounded"
                      >
                        <div>
                          <p className="font-medium capitalize">
                            {category.category}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {category.quantity} items
                          </p>
                        </div>
                        <span className="font-bold">
                          {formatCurrency(category.revenue)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No category data available
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Stylist Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UsersIcon className="h-5 w-5" />
                  Stylist Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.stylist_performance &&
                analytics.stylist_performance.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.stylist_performance.map((stylist, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-muted rounded"
                      >
                        <div>
                          <p className="font-medium">
                            Stylist {stylist.stylist_id}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {stylist.transactions} transactions
                          </p>
                        </div>
                        <span className="font-bold">
                          {formatCurrency(stylist.revenue)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No stylist data available
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Revenue Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUpIcon className="h-5 w-5" />
                Revenue Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analytics.revenue_trend && analytics.revenue_trend.length > 0 ? (
                <div className="space-y-2">
                  {analytics.revenue_trend.map((trend, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-muted rounded"
                    >
                      <span className="font-medium">
                        {trend.date
                          ? new Date(trend.date).toLocaleDateString()
                          : trend.hour !== undefined
                          ? `Hour ${trend.hour}`
                          : "N/A"}
                      </span>
                      <div className="text-right">
                        <p className="font-bold">
                          {formatCurrency(trend.revenue)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {trend.transactions} transactions
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No trend data available
                </p>
              )}
            </CardContent>
          </Card>
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No analytics data available</p>
        </div>
      )}
    </div>
  );
}
