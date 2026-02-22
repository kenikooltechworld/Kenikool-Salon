'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { WaitlistAnalyticsDashboard } from '@/components/waitlist/waitlist-analytics-dashboard';
import Link from 'next/link';

export default function WaitlistAnalyticsPage() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Waitlist Analytics</h1>
          <p className="text-gray-600 mt-1">View detailed analytics and insights about your waitlist</p>
        </div>
        <Link href="/dashboard/waitlist">
          <Button variant="outline">Back to Waitlist</Button>
        </Link>
      </div>

      {/* Analytics Dashboard */}
      <WaitlistAnalyticsDashboard />
    </div>
  );
}
