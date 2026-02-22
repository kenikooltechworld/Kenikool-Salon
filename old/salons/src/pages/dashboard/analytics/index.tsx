import React, { useState } from 'react';
import { usePeakHours, useFinancialAnalytics, useRealTimeAnalytics } from '@/lib/api/hooks/useAnalytics';
import { PeakHoursHeatmap } from '@/components/analytics/PeakHoursHeatmap';
import { FinancialTimeSeries } from '@/components/analytics/FinancialTimeSeries';
import { RealTimeDashboard } from '@/components/analytics/RealTimeDashboard';
import { format, subDays } from 'date-fns';

export default function AnalyticsDashboard() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const peakHoursQuery = usePeakHours(dateRange.start, dateRange.end);
  const financialQuery = useFinancialAnalytics(dateRange.start, dateRange.end);
  const realtimeQuery = useRealTimeAnalytics();

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    setDateRange((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time insights and performance metrics</p>
        </div>

        {/* Date Range Filter */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => handleDateChange('start', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => handleDateChange('end', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Real-Time Metrics */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Real-Time Metrics</h2>
          <RealTimeDashboard />
        </div>

        {/* Peak Hours Heatmap */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Peak Hours Analysis</h2>
          {peakHoursQuery.isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : peakHoursQuery.error ? (
            <div className="text-center py-8 text-red-600">Error loading data</div>
          ) : peakHoursQuery.data?.metrics ? (
            <PeakHoursHeatmap
              data={peakHoursQuery.data.metrics}
              onCellClick={(hour, day) => {
                console.log(`Clicked: Hour ${hour}, Day ${day}`);
              }}
            />
          ) : null}
        </div>

        {/* Financial Trends */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Financial Trends</h2>
          {financialQuery.isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : financialQuery.error ? (
            <div className="text-center py-8 text-red-600">Error loading data</div>
          ) : financialQuery.data?.metrics ? (
            <FinancialTimeSeries data={financialQuery.data.metrics} />
          ) : null}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {financialQuery.data && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Revenue</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  ${financialQuery.data.total_revenue?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Expenses</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  ${financialQuery.data.total_expenses?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Net Profit</h3>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  ${financialQuery.data.total_profit?.toFixed(2) || '0.00'}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
