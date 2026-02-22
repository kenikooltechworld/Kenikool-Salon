import React from 'react';

export default function PayrollAnalyticsPage() {
  const staffMetrics = [
    { name: 'Total Payroll', value: '$45,000', change: 5 },
    { name: 'Avg Salary', value: '$3,750', change: 2 },
    { name: 'Commission Paid', value: '$8,500', change: 12 },
    { name: 'Labor Cost %', value: '32%', change: -1 },
  ];

  const staffCommissions = [
    { name: 'Sarah Johnson', commission: 1200, bookings: 85, percentage: 14 },
    { name: 'Mike Chen', commission: 1050, bookings: 75, percentage: 12 },
    { name: 'Emma Davis', commission: 950, bookings: 68, percentage: 11 },
    { name: 'Lisa Martinez', commission: 850, bookings: 60, percentage: 10 },
  ];

  const overtimeData = [
    { week: 'Week 1', hours: 12, cost: 180 },
    { week: 'Week 2', hours: 8, cost: 120 },
    { week: 'Week 3', hours: 15, cost: 225 },
    { week: 'Week 4', hours: 10, cost: 150 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Commission & Payroll Analytics</h1>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {staffMetrics.map((metric, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-600">{metric.name}</h3>
              <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
              <p className={`text-xs mt-1 ${metric.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metric.change > 0 ? '↑' : '↓'} {Math.abs(metric.change)}%
              </p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Staff Commission Breakdown</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Staff</th>
                    <th className="text-right py-2">Commission</th>
                    <th className="text-right py-2">Bookings</th>
                  </tr>
                </thead>
                <tbody>
                  {staffCommissions.map((staff, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="py-2">{staff.name}</td>
                      <td className="text-right font-semibold">${staff.commission}</td>
                      <td className="text-right">{staff.bookings}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Overtime Analysis</h2>
            <div className="space-y-3">
              {overtimeData.map((week, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{week.week}</span>
                    <span className="text-gray-600">{week.hours}h - ${week.cost}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-orange-500"
                      style={{ width: `${(week.hours / 20) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Labor Cost Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">Cost per Booking</h3>
              <p className="text-2xl font-bold text-gray-900">$36.00</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">Revenue per Staff</h3>
              <p className="text-2xl font-bold text-gray-900">$5,625</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">Productivity Index</h3>
              <p className="text-2xl font-bold text-gray-900">92%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
