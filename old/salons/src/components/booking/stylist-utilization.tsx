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

interface StylistUtilizationData {
  name: string;
  utilization: number;
  bookedHours: number;
  availableHours: number;
  bookingCount: number;
}

interface StylistUtilizationProps {
  data: StylistUtilizationData[];
  loading?: boolean;
}

export const StylistUtilization: React.FC<StylistUtilizationProps> = ({
  data,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="text-sm text-gray-500">Loading utilization data...</div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
        No utilization data available
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Chart */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="font-medium text-gray-900 mb-4">Stylist Utilization</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
              <Bar dataKey="utilization" fill="#3b82f6" name="Utilization %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Stylist
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                Utilization
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                Booked Hours
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                Available Hours
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                Bookings
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((stylist, idx) => (
              <tr
                key={idx}
                className="border-b border-gray-200 hover:bg-gray-50"
              >
                <td className="px-4 py-3 text-sm text-gray-900">
                  {stylist.name}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          stylist.utilization >= 80
                            ? "bg-green-500"
                            : stylist.utilization >= 50
                              ? "bg-yellow-500"
                              : "bg-red-500"
                        }`}
                        style={{ width: `${stylist.utilization}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-12">
                      {stylist.utilization}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-600">
                  {stylist.bookedHours}h
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-600">
                  {stylist.availableHours}h
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-600">
                  {stylist.bookingCount}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
