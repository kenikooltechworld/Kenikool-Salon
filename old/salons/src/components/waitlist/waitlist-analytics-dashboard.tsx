'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useWaitlistAnalytics } from '@/lib/api/hooks/useWaitlist';
import { format, subDays } from 'date-fns';

export const WaitlistAnalyticsDashboard: React.FC = () => {
  const [dateFrom, setDateFrom] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
  const [dateTo, setDateTo] = useState(format(new Date(), 'yyyy-MM-dd'));
  const { data: analytics, isLoading } = useWaitlistAnalytics(dateFrom, dateTo);

  const handleExportAnalytics = () => {
    if (!analytics) return;

    const data = {
      date_range: { from: dateFrom, to: dateTo },
      stats: analytics.stats,
      service_demand: analytics.service_demand,
      stylist_demand: analytics.stylist_demand,
      conversion_metrics: analytics.conversion_metrics,
    };

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `waitlist-analytics-${format(new Date(), 'yyyy-MM-dd')}.json`;
    a.click();
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="text-center py-8 text-gray-500">No analytics data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <Card className="p-4">
        <div className="flex items-end gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">From Date</label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">To Date</label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
          <Button onClick={handleExportAnalytics} variant="outline">
            Export Analytics
          </Button>
        </div>
      </Card>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="text-sm text-gray-600 mb-2">Total Entries</div>
          <div className="text-3xl font-bold">{analytics.stats.total_waiting + analytics.stats.total_notified}</div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 mb-2">Waiting</div>
          <div className="text-3xl font-bold text-yellow-600">{analytics.stats.by_status.waiting || 0}</div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 mb-2">Notified</div>
          <div className="text-3xl font-bold text-blue-600">{analytics.stats.by_status.notified || 0}</div>
        </Card>

        <Card className="p-6">
          <div className="text-sm text-gray-600 mb-2">Avg Wait Time</div>
          <div className="text-3xl font-bold">{analytics.stats.average_wait_time.toFixed(1)} days</div>
        </Card>
      </div>

      {/* Status Breakdown */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Status Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(analytics.stats.by_status).map(([status, count]) => (
            <div key={status} className="text-center">
              <div className="text-2xl font-bold">{count}</div>
              <div className="text-sm text-gray-600 capitalize">{status}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Conversion Metrics */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Conversion Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-600 mb-2">Conversion Rate</div>
            <div className="text-4xl font-bold text-green-600">
              {(analytics.conversion_metrics.conversion_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm">Booked:</span>
              <span className="font-semibold">{analytics.conversion_metrics.booked_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Notified:</span>
              <span className="font-semibold">{analytics.conversion_metrics.notified_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Expired:</span>
              <span className="font-semibold">{analytics.conversion_metrics.expired_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Waiting:</span>
              <span className="font-semibold">{analytics.conversion_metrics.waiting_count}</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Top Services */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Top 10 Requested Services</h3>
        <div className="space-y-3">
          {analytics.service_demand.slice(0, 10).map((service, index) => (
            <div key={service.service_id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="outline">{index + 1}</Badge>
                <span>{service.service_name}</span>
              </div>
              <span className="font-semibold">{service.count} requests</span>
            </div>
          ))}
        </div>
        {analytics.service_demand.length === 0 && (
          <div className="text-center py-4 text-gray-500">No service demand data</div>
        )}
      </Card>

      {/* Top Stylists */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Top 10 Requested Stylists</h3>
        <div className="space-y-3">
          {analytics.stylist_demand.slice(0, 10).map((stylist, index) => (
            <div key={stylist.stylist_id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="outline">{index + 1}</Badge>
                <span>{stylist.stylist_name}</span>
              </div>
              <span className="font-semibold">{stylist.count} requests</span>
            </div>
          ))}
        </div>
        {analytics.stylist_demand.length === 0 && (
          <div className="text-center py-4 text-gray-500">No stylist demand data</div>
        )}
      </Card>
    </div>
  );
};
