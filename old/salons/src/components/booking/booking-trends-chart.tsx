import React from "react";
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

interface TrendData {
  date: string;
  bookings: number;
  revenue: number;
  completed: number;
  cancelled: number;
}

interface BookingTrendsChartProps {
  data: TrendData[];
  period: "daily" | "weekly" | "monthly";
  loading?: boolean;
}

export const BookingTrendsChart: React.FC<BookingTrendsChartProps> = ({
  data,
  period,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-500">
        Loading chart...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  return (
    <div className="w-full h-80 rounded-lg border border-gray-200 bg-white p-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="bookings" fill="#3b82f6" name="Total Bookings" />
          <Bar dataKey="completed" fill="#10b981" name="Completed" />
          <Bar dataKey="cancelled" fill="#ef4444" name="Cancelled" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
