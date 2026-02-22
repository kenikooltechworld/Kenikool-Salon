'use client';

import React from 'react';
import { ReviewAnalytics } from '@/components/reviews/review-analytics';
import { useAuth } from '@/lib/api/hooks/useAuth';
import { useRouter } from 'next/navigation';

export default function ReviewAnalyticsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Review Analytics</h1>
          <p className="text-gray-600 mt-2">
            Track review trends, ratings by service and stylist, and response metrics
          </p>
        </div>

        <ReviewAnalytics tenantId={user.tenant_id} />
      </div>
    </div>
  );
}
