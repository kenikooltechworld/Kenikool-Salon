import React from 'react';
import { useDemandPrediction, useChurnPrediction, useRevenuePrediction } from '@/lib/api/hooks/useAnalytics';

export default function PredictionsPage() {
  const demandQuery = useDemandPrediction(30);
  const churnQuery = useChurnPrediction();
  const revenueQuery = useRevenuePrediction(30);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Predictive Analytics</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Demand Forecast</h2>
            {demandQuery.isLoading ? (
              <div className="text-center py-4">Loading...</div>
            ) : demandQuery.error ? (
              <div className="text-center py-4 text-red-600">Error</div>
            ) : demandQuery.data ? (
              <div>
                <p className="text-sm text-gray-600">30-Day Forecast</p>
                <p className="text-2xl font-bold text-blue-600 mt-2">
                  {demandQuery.data.predictions?.[demandQuery.data.predictions.length - 1]?.toFixed(0) || 'N/A'}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Confidence: {(demandQuery.data.confidence * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500">
                  Trend: {demandQuery.data.trend}
                </p>
              </div>
            ) : null}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Churn Risk</h2>
            {churnQuery.isLoading ? (
              <div className="text-center py-4">Loading...</div>
            ) : churnQuery.error ? (
              <div className="text-center py-4 text-red-600">Error</div>
            ) : churnQuery.data ? (
              <div>
                <p className="text-sm text-gray-600">At-Risk Clients</p>
                <p className="text-2xl font-bold text-red-600 mt-2">
                  {churnQuery.data.predicted_value?.toFixed(1) || 'N/A'}%
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Confidence: {(churnQuery.data.confidence_score * 100).toFixed(0)}%
                </p>
              </div>
            ) : null}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Revenue Forecast</h2>
            {revenueQuery.isLoading ? (
              <div className="text-center py-4">Loading...</div>
            ) : revenueQuery.error ? (
              <div className="text-center py-4 text-red-600">Error</div>
            ) : revenueQuery.data ? (
              <div>
                <p className="text-sm text-gray-600">30-Day Projection</p>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  ${(revenueQuery.data.predictions?.[revenueQuery.data.predictions.length - 1] || 0).toFixed(0)}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Confidence: {(revenueQuery.data.confidence_score * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500">
                  Trend: {revenueQuery.data.trend}
                </p>
              </div>
            ) : null}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Forecast Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Demand Forecast Bounds</h3>
              {demandQuery.data && (
                <div className="text-sm text-gray-600">
                  <p>Lower: {demandQuery.data.lower_bounds?.[0]?.toFixed(0) || 'N/A'}</p>
                  <p>Upper: {demandQuery.data.upper_bounds?.[0]?.toFixed(0) || 'N/A'}</p>
                </div>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Revenue Forecast Bounds</h3>
              {revenueQuery.data && (
                <div className="text-sm text-gray-600">
                  <p>Lower: ${revenueQuery.data.lower_bounds?.[0]?.toFixed(0) || 'N/A'}</p>
                  <p>Upper: ${revenueQuery.data.upper_bounds?.[0]?.toFixed(0) || 'N/A'}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
