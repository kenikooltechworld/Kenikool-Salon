import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useGetClientFinancial,
  useGetClientPackages,
} from "@/lib/api/hooks/useClients";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DollarIcon,
  TrendingUpIcon,
  CreditCardIcon,
  PackageIcon,
} from "@/components/icons";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
} from "chart.js";
import { Bar, Pie } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  ChartLegend,
);

interface ClientFinancialSummaryProps {
  clientId: string;
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

export function ClientFinancialSummary({
  clientId,
}: ClientFinancialSummaryProps) {
  const { data: financial, isLoading: isLoadingFinancial } =
    useGetClientFinancial(clientId);
  const { data: packages, isLoading: isLoadingPackages } =
    useGetClientPackages(clientId);

  if (isLoadingFinancial) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!financial) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No financial data available
          </p>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for charts
  const revenueByMonthData = (financial.revenue_by_month || [])
    .slice(0, 6)
    .reverse();
  const revenueByCategoryData = financial.revenue_by_service_category || {};
  const paymentMethodsData = Object.values(
    financial.payment_method_preferences || {},
  );

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarIcon size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₦{financial.total_revenue.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {financial.transaction_count} transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Average Transaction
            </CardTitle>
            <TrendingUpIcon size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₦{financial.average_transaction.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">Per visit</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tips</CardTitle>
            <DollarIcon size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₦{financial.tip_total.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Avg: ₦{financial.tip_average.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Packages
            </CardTitle>
            <PackageIcon size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoadingPackages ? "..." : packages?.total_packages || 0}
            </div>
            <p className="text-xs text-muted-foreground">Package purchases</p>
          </CardContent>
        </Card>
      </div>

      {/* Revenue by Month Chart */}
      {revenueByMonthData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trend (Last 6 Months)</CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ height: "300px" }}>
              <Bar
                data={{
                  labels: revenueByMonthData.map((d) => d.month_name),
                  datasets: [
                    {
                      label: "Revenue",
                      data: revenueByMonthData.map((d) => d.revenue),
                      backgroundColor: "#8884d8",
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        callback: (value) => `₦${value.toLocaleString()}`,
                      },
                    },
                  },
                  plugins: {
                    tooltip: {
                      callbacks: {
                        label: (context) =>
                          `₦${(context.parsed.y ?? 0).toLocaleString()}`,
                      },
                    },
                  },
                }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {/* Revenue by Service Category */}
        {revenueByCategoryData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Service Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div style={{ height: "300px" }}>
                <Pie
                  data={{
                    labels: revenueByCategoryData.map((d) => d.category),
                    datasets: [
                      {
                        data: revenueByCategoryData.map((d) => d.revenue),
                        backgroundColor: COLORS,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      tooltip: {
                        callbacks: {
                          label: (context) =>
                            `₦${(context.parsed ?? 0).toLocaleString()}`,
                        },
                      },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Payment Method Preferences */}
        {paymentMethodsData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Payment Method Preferences</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {paymentMethodsData.map((method, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <CreditCardIcon
                        size={16}
                        className="text-muted-foreground"
                      />
                      <span className="text-sm font-medium capitalize">
                        {method.method}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold">
                        ₦{method.total_amount.toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {method.count} times ({method.percentage}%)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Package Purchases */}
      {!isLoadingPackages && packages && packages.packages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Package Purchases</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {packages.packages.map((pkg) => (
                <div
                  key={pkg.purchase_id}
                  className="flex items-center justify-between border-b pb-4 last:border-0"
                >
                  <div>
                    <p className="font-medium">{pkg.package_name}</p>
                    <p className="text-sm text-muted-foreground">
                      Purchased:{" "}
                      {new Date(pkg.purchase_date).toLocaleDateString()}
                    </p>
                    {pkg.expiry_date && (
                      <p className="text-xs text-muted-foreground">
                        Expires:{" "}
                        {new Date(pkg.expiry_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">
                      {pkg.remaining_sessions} / {pkg.total_sessions} sessions
                      left
                    </p>
                    <p className="text-xs text-muted-foreground">
                      ₦{pkg.purchase_price.toLocaleString()}
                    </p>
                    <span
                      className={`inline-block rounded-full px-2 py-1 text-xs ${
                        pkg.status === "active"
                          ? "bg-green-100 text-green-800"
                          : pkg.status === "expired"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {pkg.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
