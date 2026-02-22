import React, { useState } from 'react';
import { ComparativeAnalysisChart } from '@/components/analytics/ComparativeAnalysisChart';

export default function ComparativeAnalyticsPage() {
  const [comparisonType, setComparisonType] = useState<'yoy' | 'mom' | 'wow'>('yoy');

  const data = {
    yoy: [
      { period: 'Jan', current: 4500, previous: 4000 },
      { period: 'Feb', current: 5200, previous: 4800 },
      { period: 'Mar', current: 5800, previous: 5200 },
      { period: 'Apr', current: 6200, previous: 5500 },
      { period: 'May', current: 6800, previous: 6000 },
      { period: 'Jun', current: 7200, previous: 6500 },
    ],
    mom: [
      { period: 'Week 1', current: 1200, previous: 1100 },
      { period: 'Week 2', current: 1400, previous: 1300 },
      { period: 'Week 3', current: 1600, previous: 1400 },
      { period: 'Week 4', current: 1800, previous: 1700 },
    ],
    wow: [
      { period: 'Mon', current: 250, previous: 240 },
      { period: 'Tue', current: 280, previous: 270 },
      { period: 'Wed', current: 300, previous: 290 },
      { period: 'Thu', current: 320, previous: 310 },
      { period: 'Fri', current: 350, previous: 340 },
      { period: 'Sat', current: 400, previous: 380 },
      { period: 'Sun', current: 380, previous: 360 },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Comparative Analytics</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setComparisonType('yoy')}
              className={`px-4 py-2 rounded ${
                comparisonType === 'yoy'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Year-over-Year
            </button>
            <button
              onClick={() => setComparisonType('mom')}
              className={`px-4 py-2 rounded ${
                comparisonType === 'mom'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Month-over-Month
            </button>
            <button
              onClick={() => setComparisonType('wow')}
              className={`px-4 py-2 rounded ${
                comparisonType === 'wow'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Week-over-Week
            </button>
          </div>

          <ComparativeAnalysisChart
            data={data[comparisonType]}
            title={`${comparisonType.toUpperCase()} Comparison`}
          />
        </div>
      </div>
    </div>
  );
}
