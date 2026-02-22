import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface RevenueData {
  name: string;
  value: number;
  percentage: number;
}

interface RevenueAnalyticsProps {
  byService?: RevenueData[];
  byStylist?: RevenueData[];
  byLocation?: RevenueData[];
  totalRevenue: number;
  loading?: boolean;
}

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
];

export const RevenueAnalytics: React.FC<RevenueAnalyticsProps> = ({
  byService = [],
  byStylist = [],
  byLocation = [],
  totalRevenue,
  loading = false,
}) => {
  if (loading) {
    return <div className="text-sm text-gray-500">Loading analytics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Total Revenue */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="font-medium text-gray-900">Total Revenue</h3>
        <p className="text-3xl font-bold text-green-600 mt-2">
          ${totalRevenue.toFixed(2)}
        </p>
      </div>

      {/* By Service */}
      {byService.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="font-medium text-gray-900 mb-4">Revenue by Service</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={byService}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {byService.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* By Stylist */}
      {byStylist.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="font-medium text-gray-900 mb-4">Revenue by Stylist</h3>
          <div className="space-y-2">
            {byStylist.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{item.name}</span>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    ${item.value.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">{item.percentage}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* By Location */}
      {byLocation.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="font-medium text-gray-900 mb-4">
            Revenue by Location
          </h3>
          <div className="space-y-2">
            {byLocation.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{item.name}</span>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    ${item.value.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">{item.percentage}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
