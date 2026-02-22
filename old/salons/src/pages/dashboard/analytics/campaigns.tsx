import React, { useState } from 'react';
import { useCampaignAnalytics } from '@/lib/api/hooks/useAnalytics';
import { format, subDays } from 'date-fns';

export default function CampaignAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const query = useCampaignAnalytics(dateRange.start, dateRange.end);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Campaign Analytics</h1>

        {query.isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : query.error ? (
          <div className="text-center py-8 text-red-600">Error loading data</div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              {query.data && (
                <>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600">Total ROI</h3>
                    <p className="text-2xl font-bold text-green-600 mt-2">
                      {query.data.total_roi?.toFixed(1) || '0'}%
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600">Total Cost</h3>
                    <p className="text-2xl font-bold text-red-600 mt-2">
                      ${query.data.total_cost?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600">Total Revenue</h3>
                    <p className="text-2xl font-bold text-blue-600 mt-2">
                      ${query.data.total_revenue?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600">Campaigns</h3>
                    <p className="text-2xl font-bold text-purple-600 mt-2">
                      {query.data.campaigns?.length || 0}
                    </p>
                  </div>
                </>
              )}
            </div>

            {query.data?.campaigns && query.data.campaigns.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Campaign Performance</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-4">Campaign</th>
                        <th className="text-left py-2 px-4">Impressions</th>
                        <th className="text-left py-2 px-4">Clicks</th>
                        <th className="text-left py-2 px-4">Conversions</th>
                        <th className="text-left py-2 px-4">Cost</th>
                        <th className="text-left py-2 px-4">Revenue</th>
                        <th className="text-left py-2 px-4">ROI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {query.data.campaigns.map((campaign, idx) => (
                        <tr key={idx} className="border-b hover:bg-gray-50">
                          <td className="py-2 px-4">{campaign.campaign_name}</td>
                          <td className="py-2 px-4">{campaign.impressions?.toLocaleString()}</td>
                          <td className="py-2 px-4">{campaign.clicks?.toLocaleString()}</td>
                          <td className="py-2 px-4">{campaign.conversions?.toLocaleString()}</td>
                          <td className="py-2 px-4">${campaign.cost?.toFixed(2)}</td>
                          <td className="py-2 px-4">${campaign.revenue?.toFixed(2)}</td>
                          <td className="py-2 px-4 font-bold text-green-600">
                            {campaign.roi?.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
