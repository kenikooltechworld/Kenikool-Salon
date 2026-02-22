'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Download, Calendar } from 'lucide-react';

interface AnalyticsData {
  total_sold: number;
  total_redeemed: number;
  outstanding_liability: number;
  redemption_rate: number;
  expiration_rate: number;
  average_card_value: number;
  total_cards_created: number;
  total_cards_redeemed: number;
  total_cards_expired: number;
  card_type_breakdown: {
    digital: number;
    physical: number;
  };
  top_purchasers: Array<{ name: string; count: number; amount: number }>;
  top_recipients: Array<{ name: string; count: number; amount: number }>;
}

interface AnalyticsProps {
  tenantId: string;
}

export default function GiftCardAnalytics({ tenantId }: AnalyticsProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        tenant_id: tenantId,
      });

      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await fetch(`/api/pos/gift-cards/analytics?${params}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load analytics');
      }

      const analyticsData: AnalyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams({
        tenant_id: tenantId,
        format: 'csv',
      });

      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await fetch(`/api/pos/gift-cards/analytics/export?${params}`);

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Failed to export CSV:', err);
    }
  };

  const handleExportPDF = async () => {
    try {
      const params = new URLSearchParams({
        tenant_id: tenantId,
        format: 'pdf',
      });

      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await fetch(`/api/pos/gift-cards/analytics/export?${params}`);

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Failed to export PDF:', err);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-12 pb-12 text-center">
          <p className="text-gray-600">Loading analytics...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertCircle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-12 pb-12 text-center">
          <p className="text-gray-600">No analytics data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gift Card Analytics</h1>
          <p className="text-gray-600 mt-1">Performance metrics and insights</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportCSV}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={handleExportPDF}>
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Date Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="dateFrom" className="block text-sm font-medium text-gray-700 mb-2">
                From
              </label>
              <input
                id="dateFrom"
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div>
              <label htmlFor="dateTo" className="block text-sm font-medium text-gray-700 mb-2">
                To
              </label>
              <input
                id="dateTo"
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <div className="flex items-end">
              <Button onClick={loadAnalytics} className="w-full">
                <Calendar className="w-4 h-4 mr-2" />
                Apply Filter
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Sold</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              {formatCurrency(data.total_sold)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {data.total_cards_created} cards created
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Redeemed</p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              {formatCurrency(data.total_redeemed)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {data.total_cards_redeemed} cards redeemed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Outstanding Liability</p>
            <p className="text-2xl font-bold text-orange-600 mt-2">
              {formatCurrency(data.outstanding_liability)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Unredeemed balance
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Rates and Percentages */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Redemption Rate</p>
            <p className="text-2xl font-bold text-blue-600 mt-2">
              {data.redemption_rate.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Of sold value redeemed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Expiration Rate</p>
            <p className="text-2xl font-bold text-red-600 mt-2">
              {data.expiration_rate.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {data.total_cards_expired} cards expired
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Average Card Value</p>
            <p className="text-2xl font-bold text-purple-600 mt-2">
              {formatCurrency(data.average_card_value)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Per card created
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Card Type Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Card Type Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Digital Cards</p>
              <p className="text-2xl font-bold text-blue-600 mt-2">
                {data.card_type_breakdown.digital}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Physical Cards</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                {data.card_type_breakdown.physical}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Top Purchasers */}
      {data.top_purchasers && data.top_purchasers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top Purchasers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.top_purchasers.map((purchaser, idx) => (
                <div key={idx} className="flex justify-between items-center pb-3 border-b last:border-b-0">
                  <div>
                    <p className="font-semibold text-gray-900">{purchaser.name}</p>
                    <p className="text-xs text-gray-500">{purchaser.count} purchases</p>
                  </div>
                  <p className="font-semibold text-gray-900">
                    {formatCurrency(purchaser.amount)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Recipients */}
      {data.top_recipients && data.top_recipients.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top Recipients</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.top_recipients.map((recipient, idx) => (
                <div key={idx} className="flex justify-between items-center pb-3 border-b last:border-b-0">
                  <div>
                    <p className="font-semibold text-gray-900">{recipient.name}</p>
                    <p className="text-xs text-gray-500">{recipient.count} cards received</p>
                  </div>
                  <p className="font-semibold text-gray-900">
                    {formatCurrency(recipient.amount)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
