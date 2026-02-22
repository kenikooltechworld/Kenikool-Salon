import React, { useState } from 'react';
import { useInventoryAnalytics } from '@/lib/api/hooks/useAnalytics';
import { InventoryBoxPlot } from '@/components/analytics/InventoryBoxPlot';
import { format, subDays } from 'date-fns';

export default function InventoryAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const query = useInventoryAnalytics(dateRange.start, dateRange.end);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Inventory Analytics</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Distribution Analysis</h2>
          {query.isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : query.error ? (
            <div className="text-center py-8 text-red-600">Error loading data</div>
          ) : (
            <InventoryBoxPlot />
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {query.data && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Inventory Value</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  ${query.data.total_inventory_value?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Forecast Accuracy</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {(query.data.forecast_accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Fast Moving Items</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {query.data.fast_moving_items?.length || 0}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
