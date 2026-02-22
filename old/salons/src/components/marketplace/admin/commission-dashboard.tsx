import { useState } from "react";
import { motion } from "framer-motion";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { useCommissionDashboard } from "@/lib/api/hooks/useMarketplaceQueries";
import { TrendingUpIcon, DollarSignIcon, UsersIcon, ShoppingCartIcon } from "@/components/icons";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface MetricCard {
  label: string;
  value: string;
  change: number;
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

export function CommissionDashboard() {
  const { data: dashboardData, isLoading } = useCommissionDashboard();
  const [dateRange, setDateRange] = useState<"week" | "month" | "year">("month");

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)] mx-auto mb-4"></div>
          <p className="text-[var(--muted-foreground)]">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Failed to load dashboard data</p>
      </div>
    );
  }

  const metrics: MetricCard[] = [
    {
      label: "Total Commission",
      value: `₦${dashboardData.total_commission.toLocaleString()}`,
      change: dashboardData.commission_growth || 0,
      icon: DollarSignIcon,
    },
    {
      label: "This Month",
      value: `₦${dashboardData.commission_this_month.toLocaleString()}`,
      change: dashboardData.month_growth || 0,
      icon: TrendingUpIcon,
    },
    {
      label: "Total Bookings",
      value: dashboardData.total_bookings.toLocaleString(),
      change: dashboardData.booking_growth || 0,
      icon: ShoppingCartIcon,
    },
    {
      label: "Active Salons",
      value: dashboardData.active_salons.toLocaleString(),
      change: dashboardData.salon_growth || 0,
      icon: UsersIcon,
    },
  ];

  // Chart data
  const commissionTrendData = {
    labels: dashboardData.commission_trend?.labels || [],
    datasets: [
      {
        label: "Commission Earned",
        data: dashboardData.commission_trend?.data || [],
        borderColor: "rgb(59, 130, 246)",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const commissionByTypeData = {
    labels: dashboardData.commission_by_type?.labels || [],
    datasets: [
      {
        label: "Commission by Type",
        data: dashboardData.commission_by_type?.data || [],
        backgroundColor: [
          "rgba(59, 130, 246, 0.8)",
          "rgba(34, 197, 94, 0.8)",
          "rgba(249, 115, 22, 0.8)",
          "rgba(168, 85, 247, 0.8)",
        ],
      },
    ],
  };

  const topSalonsData = {
    labels: dashboardData.top_salons?.map((s: any) => s.name) || [],
    datasets: [
      {
        label: "Commission Earned",
        data: dashboardData.top_salons?.map((s: any) => s.commission) || [],
        backgroundColor: "rgba(59, 130, 246, 0.8)",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: "top" as const,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Date Range Filter */}
      <motion.div
        className="flex gap-2"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {(["week", "month", "year"] as const).map((range) => (
          <motion.button
            key={range}
            onClick={() => setDateRange(range)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              dateRange === range
                ? "bg-[var(--primary)] text-white"
                : "bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--border)]"
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {range.charAt(0).toUpperCase() + range.slice(1)}
          </motion.button>
        ))}
      </motion.div>

      {/* Metric Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, staggerChildren: 0.1 }}
      >
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const isPositive = metric.change >= 0;

          return (
            <motion.div
              key={metric.label}
              className="bg-white rounded-lg border border-[var(--border)] p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-[var(--primary)]/10 rounded-lg">
                  <Icon size={24} className="text-[var(--primary)]" />
                </div>
                <div
                  className={`text-sm font-semibold ${
                    isPositive ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {isPositive ? "+" : ""}{metric.change}%
                </div>
              </div>
              <p className="text-sm text-[var(--muted-foreground)] mb-1">
                {metric.label}
              </p>
              <p className="text-2xl font-bold text-[var(--foreground)]">
                {metric.value}
              </p>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Charts */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, staggerChildren: 0.1 }}
      >
        {/* Commission Trend */}
        <motion.div
          className="bg-white rounded-lg border border-[var(--border)] p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4">
            Commission Trend
          </h3>
          <div className="h-80">
            <Line data={commissionTrendData} options={chartOptions} />
          </div>
        </motion.div>

        {/* Commission by Type */}
        <motion.div
          className="bg-white rounded-lg border border-[var(--border)] p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4">
            Commission by Type
          </h3>
          <div className="h-80 flex items-center justify-center">
            <Doughnut data={commissionByTypeData} options={chartOptions} />
          </div>
        </motion.div>
      </motion.div>

      {/* Top Salons */}
      <motion.div
        className="bg-white rounded-lg border border-[var(--border)] p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4">
          Top Salons by Commission
        </h3>
        <div className="h-80">
          <Bar data={topSalonsData} options={chartOptions} />
        </div>
      </motion.div>

      {/* Summary Stats */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7, staggerChildren: 0.1 }}
      >
        {[
          {
            label: "Average Commission per Booking",
            value: `₦${dashboardData.average_commission_per_booking?.toLocaleString() || "0"}`,
          },
          {
            label: "Highest Commission Rate",
            value: `${dashboardData.highest_commission_rate || "0"}%`,
          },
          {
            label: "Lowest Commission Rate",
            value: `${dashboardData.lowest_commission_rate || "0"}%`,
          },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            className="bg-gradient-to-br from-[var(--primary)]/10 to-[var(--primary)]/5 rounded-lg border border-[var(--primary)]/20 p-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 + index * 0.1 }}
          >
            <p className="text-sm text-[var(--muted-foreground)] mb-1">
              {stat.label}
            </p>
            <p className="text-2xl font-bold text-[var(--primary)]">
              {stat.value}
            </p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
