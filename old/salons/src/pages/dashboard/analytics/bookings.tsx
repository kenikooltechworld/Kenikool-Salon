import React from 'react';

export default function BookingAnalyticsPage() {
  const bookingMetrics = [
    { label: 'Total Bookings', value: 1250, change: 12 },
    { label: 'Cancellations', value: 45, change: -8 },
    { label: 'No-Shows', value: 23, change: -5 },
    { label: 'Conversion Rate', value: '94.5%', change: 2.3 },
  ];

  const bookingSources = [
    { source: 'Website', count: 450, percentage: 36 },
    { source: 'Phone', count: 380, percentage: 30 },
    { source: 'Walk-in', count: 250, percentage: 20 },
    { source: 'Referral', count: 170, percentage: 14 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Booking Analytics</h1>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {bookingMetrics.map((metric, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-600">{metric.label}</h3>
              <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
              <p className={`text-xs mt-1 ${metric.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metric.change > 0 ? '↑' : '↓'} {Math.abs(metric.change)}%
              </p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Booking Sources</h2>
            <div className="space-y-3">
              {bookingSources.map((source, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{source.source}</span>
                    <span className="text-gray-600">{source.count} ({source.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${source.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Lead Time Analysis</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-700">Same Day</span>
                <span className="font-semibold">15%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">1-7 Days</span>
                <span className="font-semibold">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">1-4 Weeks</span>
                <span className="font-semibold">30%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">1+ Months</span>
                <span className="font-semibold">10%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
