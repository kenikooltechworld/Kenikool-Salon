import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useGetDailySummary } from "@/lib/api/hooks/usePOS";
import {
  DollarSignIcon,
  TrendingUpIcon,
  ShoppingCartIcon,
  CreditCardIcon,
  CalendarIcon,
} from "@/components/icons";
import { toast } from "sonner";

export default function POSReportsPage() {
  const today = new Date().toISOString().split("T")[0];
  const [selectedDate, setSelectedDate] = useState(today);
  const {
    data: summary,
    isLoading,
    refetch,
  } = useGetDailySummary(selectedDate);

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
  };

  const handleRefresh = () => {
    refetch();
    toast.success("Report refreshed");
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Daily Summary Reports</h1>
          <p className="text-muted-foreground">
            View sales and transaction summaries
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline">
          Refresh
        </Button>
      </div>

      {/* Date Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <CalendarIcon className="h-5 w-5 text-muted-foreground" />
            <div className="flex-1 max-w-xs">
              <Label htmlFor="report-date">Select Date</Label>
              <Input
                id="report-date"
                type="date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
                max={today}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading report...</p>
        </div>
      )}

      {/* Summary Cards */}
      {!isLoading && summary && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Sales */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Sales
                </CardTitle>
                <DollarSignIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ₦{(summary.total_sales || 0).toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Gross revenue
                </p>
              </CardContent>
            </Card>

            {/* Transaction Count */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Transactions
                </CardTitle>
                <ShoppingCartIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summary.transaction_count || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Completed sales
                </p>
              </CardContent>
            </Card>

            {/* Average Transaction */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Avg Transaction
                </CardTitle>
                <TrendingUpIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ₦{(summary.average_transaction || 0).toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Per sale</p>
              </CardContent>
            </Card>

            {/* Total Tips */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Tips
                </CardTitle>
                <CreditCardIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ₦{(summary.total_tips || 0).toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Gratuities</p>
              </CardContent>
            </Card>
          </div>

          {/* Payment Methods Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Methods</CardTitle>
            </CardHeader>
            <CardContent>
              {(summary.payment_methods || []).length === 0 ? (
                <p className="text-center text-muted-foreground py-4">
                  No payment methods recorded
                </p>
              ) : (
                <div className="space-y-3">
                  {(summary.payment_methods || []).map(
                    (method: {
                      method: string;
                      count: number;
                      total: number;
                    }) => (
                      <div
                        key={method.method}
                        className="flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <CreditCardIcon className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium capitalize">
                              {method.method}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {method.count} transactions
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">
                            ₦{(method.total || 0).toFixed(2)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {(
                              ((method.total || 0) /
                                (summary.total_sales || 1)) *
                              100
                            ).toFixed(1)}
                            %
                          </p>
                        </div>
                      </div>
                    )
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Services vs Products */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Services</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Revenue:</span>
                    <span className="font-bold">
                      ₦{(summary.services_revenue || 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Count:</span>
                    <span className="font-bold">{summary.services_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Products</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Revenue:</span>
                    <span className="font-bold">
                      ₦{(summary.products_revenue || 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Count:</span>
                    <span className="font-bold">{summary.products_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Discounts and Taxes */}
          <Card>
            <CardHeader>
              <CardTitle>Additional Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Total Discounts
                  </p>
                  <p className="text-2xl font-bold text-red-600">
                    -₦{(summary.total_discounts || 0).toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Tax</p>
                  <p className="text-2xl font-bold">
                    ₦{(summary.total_tax || 0).toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Net Sales</p>
                  <p className="text-2xl font-bold text-green-600">
                    ₦
                    {(
                      (summary.total_sales || 0) -
                      (summary.total_discounts || 0)
                    ).toFixed(2)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* No Data State */}
      {!isLoading && !summary && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No transactions found for this date
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
