import React, { useState, useEffect } from 'react';
import { useRealTimeAnalyticsWebSocket } from '@/lib/api/hooks/useAnalytics';

interface MetricCard {
  label: string;
  value: number | string;
  unit?: string;
  change?: number;
  status?: 'normal' | 'warning' | 'critical';
}

export const RealTimeDashboard: React.FC = () => {
  const { data, isConnected, error } = useRealTimeAnalyticsWebSocket();
  const [metrics, setMetrics] = useState<MetricCard[]>([]);

  useEffect(() => {
    if (data) {
      setMetrics([
        {
          label: 'Active Bookings',
          value: data.active_bookings || 0,
          status: data.active_bookings > 10 ? 'normal' : 'warning',
        },
        {
          label: 'Current Revenue',
          value: `$${(data.current_revenue || 0).toFixed(2)}`,
          status: data.current_revenue > 2000 ? 'normal' : 'warning',
        },
        {
          label: 'Staff Utilization',
          value: `${((data.staff_utilization || 0) * 100).toFixed(1)}%`,
          status: data.staff_utilization > 0.8 ? 'normal' : 'warning',
        },
        {
          label: 'Queue Length',
          value: data.queue_length || 0,
          status: data.queue_length > 5 ? 'critical' : data.queue_length > 2 ? 'warning' : 'normal',
        },
      ]);
    }
  }, [data]);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'critical':
        return 'bg-red-100 border-red-300';
      case 'warning':
        return 'bg-yellow-100 border-yellow-300';
      default:
        return 'bg-green-100 border-green-300';
    }
  };

  const getStatusTextColor = (status?: string) => {
    switch (status) {
      case 'critical':
        return 'text-red-700';
      case 'warning':
        return 'text-yellow-700';
      default:
        return 'text-green-700';
    }
  };

  return (
    <div className="w-full">
      {/* Connection Status */}
      <div className="mb-4 flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`}
        />
        <span className="text-sm font-medium">
          {isConnected ? 'Live' : 'Disconnected'}
        </span>
        {error && <span className="text-sm text-red-600">{error}</span>}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border-2 ${getStatusColor(metric.status)}`}
          >
            <p className="text-sm font-medium text-gray-600">{metric.label}</p>
            <p className={`text-2xl font-bold mt-2 ${getStatusTextColor(metric.status)}`}>
              {metric.value}
            </p>
            {metric.change !== undefined && (
              <p className="text-xs mt-2 text-gray-500">
                {metric.change > 0 ? '↑' : '↓'} {Math.abs(metric.change).toFixed(1)}%
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Last Updated */}
      <div className="mt-4 text-xs text-gray-500">
        Last updated: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
      </div>
    </div>
  );
};
