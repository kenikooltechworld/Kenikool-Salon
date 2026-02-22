import React, { useState } from 'react';
import { useFinancialAnalytics } from '@/lib/api/hooks/useAnalytics';
import { FinancialTimeSeries } from '@/components/analytics/FinancialTimeSeries';
import { RevenueTreemap } from '@/components/analytics/RevenueTreemap';
import { format, subDays } from 'date-fns';

export default function FinancialAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const query = useFinancialAnalytics(dateRange.start, dateRange.end);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Financial Analytics</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Financial Trends</h2>
          {query.isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : query.error ? (
            <div className="text-center py-8 text-red-600">Error loading data</div>
          ) : query.data?.metrics ? (
            <FinancialTimeSeries data={query.data.metrics} />
          ) : null}
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Revenue Breakdown</h2>
          <RevenueTreemap />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {query.data && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Revenue</h3>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  ${query.data.total_revenue?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Expenses</h3>
                <p className="text-2xl font-bold text-red-600 mt-2">
                  ${query.data.total_expenses?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Net Profit</h3>
                <p className="text-2xl font-bold text-blue-600 mt-2">
                  ${query.data.total_profit?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Profit Margin</h3>
                <p className="text-2xl font-bold text-purple-600 mt-2">
                  {query.data.average_margin?.toFixed(1) || '0'}%
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
