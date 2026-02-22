import React, { useState } from 'react';
import { useClientAnalytics } from '@/lib/api/hooks/useAnalytics';
import { ClientCohortAnalysis } from '@/components/analytics/ClientCohortAnalysis';
import { LTVDistributionChart } from '@/components/analytics/LTVDistributionChart';
import { format, subDays } from 'date-fns';

export default function ClientAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const query = useClientAnalytics(dateRange.start, dateRange.end);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Client Analytics</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Cohort Retention Analysis</h2>
          {query.isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : query.error ? (
            <div className="text-center py-8 text-red-600">Error loading data</div>
          ) : (
            <ClientCohortAnalysis />
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Lifetime Value Distribution</h2>
          <LTVDistributionChart />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {query.data && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Total Clients</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {query.data.total_clients || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">New Clients</h3>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  {query.data.new_clients || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">At Risk</h3>
                <p className="text-2xl font-bold text-red-600 mt-2">
                  {query.data.at_risk_count || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-600">Average LTV</h3>
                <p className="text-2xl font-bold text-blue-600 mt-2">
                  ${query.data.average_ltv?.toFixed(0) || '0'}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
