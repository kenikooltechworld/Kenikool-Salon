import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Select } from "@/components/ui/select";
import {
  DollarSignIcon,
  CalendarIcon,
  FilterIcon,
  RefreshCwIcon,
  HistoryIcon,
  PercentIcon,
  ReceiptIcon,
  TrendingUpIcon,
  InfoIcon,
  AlertCircleIcon,
  CheckCircleIcon,
} from "@/components/icons";
import { StaffEarningsChart } from "@/components/staff/StaffEarningsChart";
import { StaffEarningsBreakdown } from "@/components/staff/StaffEarningsBreakdown";
import { useMyEarnings, useMyEarningsSummary } from "@/hooks/useMyEarnings";
import { getMonthStart, getMonthEnd, addDays } from "@/lib/utils/date";

interface DateRange {
  startDate: string;
  endDate: string;
}

interface BreakdownType {
  value: "service" | "date";
  label: string;
}

interface TimePeriod {
  value: string;
  label: string;
  getRange: () => DateRange;
}

const breakdownTypes: BreakdownType[] = [
  { value: "service", label: "By Service Type" },
  { value: "date", label: "By Date Range" },
];

const timePeriods: TimePeriod[] = [
  {
    value: "this_month",
    label: "This Month",
    getRange: () => {
      const now = new Date();
      const start = getMonthStart(now);
      const end = getMonthEnd(now);
      return {
        startDate: start.toISOString().split("T")[0],
        endDate: end.toISOString().split("T")[0],
      };
    },
  },
  {
    value: "last_month",
    label: "Last Month",
    getRange: () => {
      const now = new Date();
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const start = getMonthStart(lastMonth);
      const end = getMonthEnd(lastMonth);
      return {
        startDate: start.toISOString().split("T")[0],
        endDate: end.toISOString().split("T")[0],
      };
    },
  },
  {
    value: "last_30_days",
    label: "Last 30 Days",
    getRange: () => {
      const now = new Date();
      const start = addDays(now, -30);
      return {
        startDate: start.toISOString().split("T")[0],
        endDate: now.toISOString().split("T")[0],
      };
    },
  },
  {
    value: "last_90_days",
    label: "Last 90 Days",
    getRange: () => {
      const now = new Date();
      const start = addDays(now, -90);
      return {
        startDate: start.toISOString().split("T")[0],
        endDate: now.toISOString().split("T")[0],
      };
    },
  },
  {
    value: "custom",
    label: "Custom Range",
    getRange: () => ({
      startDate: "",
      endDate: "",
    }),
  },
];

/**
 * My Earnings page for staff members
 * Displays earnings data, commission information, and payment history
 * Includes filtering by date range and breakdown by service type
 *
 * Features:
 * - Total earnings summary for current period
 * - Earnings breakdown by service type and date range
 * - Payment history with transaction details
 * - Date range filtering (daily, weekly, monthly)
 * - Commission rate information display
 * - Responsive design for mobile devices
 * - Proper error handling and loading states
 */
export default function Earnings() {
  const [selectedPeriod, setSelectedPeriod] = useState("this_month");
  const [breakdownType, setBreakdownType] = useState<"service" | "date">(
    "service",
  );
  const [customDateRange, setCustomDateRange] = useState<DateRange>({
    startDate: "",
    endDate: "",
  });

  // Get date range based on selected period
  const getDateRange = (): DateRange => {
    if (selectedPeriod === "custom") {
      return customDateRange;
    }
    const period = timePeriods.find((p) => p.value === selectedPeriod);
    return period?.getRange() || timePeriods[0].getRange();
  };

  const dateRange = getDateRange();
  const hasValidDateRange =
    dateRange.startDate &&
    dateRange.endDate &&
    dateRange.startDate <= dateRange.endDate;

  // Fetch earnings data
  const {
    data: earningsData,
    isLoading: earningsLoading,
    error: earningsError,
    refetch: refetchEarnings,
  } = useMyEarnings(hasValidDateRange ? dateRange : undefined);

  const {
    data: summaryData,
    isLoading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useMyEarningsSummary();

  const handleRefresh = () => {
    refetchEarnings();
    refetchSummary();
  };

  const handlePeriodChange = (value: string) => {
    setSelectedPeriod(value);
    if (value !== "custom") {
      setCustomDateRange({ startDate: "", endDate: "" });
    }
  };

  const handleCustomDateChange = (
    field: "startDate" | "endDate",
    value: string,
  ) => {
    setCustomDateRange((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const isLoading = earningsLoading || summaryLoading;
  const commissions = earningsData?.commissions || [];
  const hasEarningsData = commissions.length > 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <DollarSignIcon size={28} className="text-primary" />
            My Earnings
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your commission and earnings details
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            disabled={isLoading}
            className="self-start sm:self-auto"
          >
            <RefreshCwIcon size={16} className="mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Earnings Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Total Earnings */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSignIcon size={16} />
              Total Earnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : summaryError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  ₦
                  {(summaryData?.totalEarnings || 0).toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p className="text-xs text-muted-foreground mt-1">All time</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* This Month */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CalendarIcon size={16} />
              This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : summaryError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  ₦
                  {(summaryData?.thisMonth || 0).toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Current month
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* This Week */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUpIcon size={16} />
              This Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : summaryError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  ₦
                  {(summaryData?.thisWeek || 0).toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Current week
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <FilterIcon size={20} />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Time Period Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Time Period
              </label>
              <Select value={selectedPeriod} onValueChange={handlePeriodChange}>
                {timePeriods.map((period) => (
                  <option key={period.value} value={period.value}>
                    {period.label}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Breakdown Type
              </label>
              <Select
                value={breakdownType}
                onValueChange={(value) =>
                  setBreakdownType(value as "service" | "date")
                }
              >
                {breakdownTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Custom Date Range */}
          {selectedPeriod === "custom" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-border">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Start Date
                </label>
                <input
                  type="date"
                  value={customDateRange.startDate}
                  onChange={(e) =>
                    handleCustomDateChange("startDate", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  max={customDateRange.endDate || undefined}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  End Date
                </label>
                <input
                  type="date"
                  value={customDateRange.endDate}
                  onChange={(e) =>
                    handleCustomDateChange("endDate", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  min={customDateRange.startDate || undefined}
                />
              </div>
            </div>
          )}

          {/* Date Range Display */}
          {hasValidDateRange && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CalendarIcon size={16} />
              <span>
                Showing data from{" "}
                {new Date(dateRange.startDate).toLocaleDateString("en-NG")} to{" "}
                {new Date(dateRange.endDate).toLocaleDateString("en-NG")}
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charts and Breakdown */}
      {hasValidDateRange ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Earnings Chart */}
          <StaffEarningsChart
            commissions={commissions}
            isLoading={earningsLoading}
            error={earningsError?.message}
            onRetry={refetchEarnings}
            period={dateRange}
          />

          {/* Earnings Breakdown */}
          <StaffEarningsBreakdown
            commissions={commissions}
            isLoading={earningsLoading}
            error={earningsError?.message}
            onRetry={refetchEarnings}
            breakdownType={breakdownType}
          />
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <CalendarIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Select Date Range
            </h3>
            <p className="text-muted-foreground">
              Choose a time period to view your earnings data and charts
            </p>
          </CardContent>
        </Card>
      )}

      {/* Commission Rate Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <PercentIcon size={20} />
            Commission Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-foreground flex items-center gap-2">
                <CheckCircleIcon size={16} className="text-green-500" />
                Commission Structure
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">
                    Percentage Rate:
                  </span>
                  <Badge variant="secondary" className="font-medium">
                    15%
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Fixed Rate:</span>
                  <Badge variant="secondary" className="font-medium">
                    ₦500 per service
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">
                    Payment Schedule:
                  </span>
                  <Badge variant="default" className="font-medium">
                    Weekly
                  </Badge>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium text-foreground flex items-center gap-2">
                <InfoIcon size={16} className="text-blue-500" />
                Payment Information
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Next Payment:</span>
                  <span className="font-medium">
                    {new Date(
                      Date.now() + 7 * 24 * 60 * 60 * 1000,
                    ).toLocaleDateString("en-NG")}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Payment Method:</span>
                  <Badge variant="outline" className="font-medium">
                    Bank Transfer
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge
                    variant="default"
                    className="font-medium text-green-700 bg-green-100"
                  >
                    Active
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <HistoryIcon size={20} />
            Payment History
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Recent commission payments and transaction details
          </p>
        </CardHeader>
        <CardContent>
          {hasValidDateRange && hasEarningsData ? (
            <div className="space-y-3">
              {commissions.slice(0, 10).map((commission) => (
                <div
                  key={commission.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3 mb-2 sm:mb-0">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                      <ReceiptIcon size={20} className="text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-foreground truncate">
                        Transaction #{commission.transaction_id.slice(-8)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(commission.calculated_at).toLocaleDateString(
                          "en-NG",
                          {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between sm:justify-end gap-4">
                    <div className="text-right">
                      <p className="font-bold text-foreground">
                        ₦
                        {commission.commission_amount.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {commission.commission_type === "percentage"
                          ? `${commission.commission_rate}% commission`
                          : "Fixed rate"}
                      </p>
                    </div>
                    <Badge
                      variant={
                        commission.commission_type === "percentage"
                          ? "default"
                          : "secondary"
                      }
                      className="text-xs"
                    >
                      {commission.commission_type === "percentage"
                        ? `${commission.commission_rate}%`
                        : "Fixed"}
                    </Badge>
                  </div>
                </div>
              ))}
              {commissions.length > 10 && (
                <div className="text-center pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground">
                    Showing 10 of {commissions.length} transactions for selected
                    period
                  </p>
                  <Button variant="outline" size="sm" className="mt-2">
                    View All Transactions
                  </Button>
                </div>
              )}
            </div>
          ) : hasValidDateRange && !hasEarningsData ? (
            <div className="text-center py-12">
              <ReceiptIcon
                size={48}
                className="mx-auto text-muted-foreground mb-4"
              />
              <h3 className="text-lg font-medium text-foreground mb-2">
                No Earnings Recorded
              </h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                No commission payments found for the selected period. Complete
                appointments to start earning commissions.
              </p>
            </div>
          ) : (
            <div className="text-center py-12">
              <InfoIcon
                size={48}
                className="mx-auto text-muted-foreground mb-4"
              />
              <h3 className="text-lg font-medium text-foreground mb-2">
                Select Date Range
              </h3>
              <p className="text-muted-foreground">
                Choose a time period to view your payment history and
                transaction details
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
