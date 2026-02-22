'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Search, AlertCircle, CheckCircle } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { useGiftCardBalance } from '@/lib/api/hooks/useGiftCards';

export default function BalanceCheckPage() {
  const searchParams = useSearchParams();
  const [cardNumber, setCardNumber] = useState(searchParams.get('card') || '');
  const [tenantId, setTenantId] = useState(searchParams.get('tenant') || '');
  const { checkBalance, loading, error, data: balanceInfo } = useGiftCardBalance();

  const handleCheckBalance = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (!cardNumber.trim()) {
        throw new Error('Please enter a gift card number');
      }

      if (!tenantId.trim()) {
        throw new Error('Please enter a tenant ID');
      }

      await checkBalance({ cardNumber, tenantId });
    } catch (err) {
      // Error is handled by the hook
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600';
      case 'expired':
        return 'text-red-600';
      case 'inactive':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Active</span>;
      case 'expired':
        return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-red-100 text-red-800 text-sm font-medium"><AlertCircle className="w-4 h-4" /> Expired</span>;
      case 'inactive':
        return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 text-sm font-medium">Inactive</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 text-gray-800 text-sm font-medium">{status}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/gift-cards" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Gift Cards
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Check Balance</h1>
          <p className="text-gray-600 mt-2">Enter your gift card number to check your balance</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <CardHeader>
            <CardTitle>Gift Card Balance Lookup</CardTitle>
            <CardDescription>No login required - just enter your card details</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCheckBalance} className="space-y-6">
              {/* Card Number Input */}
              <div>
                <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-2">
                  Gift Card Number
                </label>
                <Input
                  id="cardNumber"
                  type="text"
                  placeholder="e.g., GC-1234567890AB"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  disabled={loading}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">
                  You can find this on your gift card or email receipt
                </p>
              </div>

              {/* Tenant ID Input */}
              <div>
                <label htmlFor="tenantId" className="block text-sm font-medium text-gray-700 mb-2">
                  Salon ID
                </label>
                <Input
                  id="tenantId"
                  type="text"
                  placeholder="Enter salon ID"
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  disabled={loading}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Ask the salon staff if you don't have this
                </p>
              </div>

              {/* Error Alert */}
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Checking Balance...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Check Balance
                  </>
                )}
              </Button>
            </form>

            {/* Balance Result */}
            {balanceInfo && (
              <div className="mt-8 pt-8 border-t">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Your Balance</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Balance Card */}
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
                    <p className="text-sm text-gray-600 mb-2">Current Balance</p>
                    <p className="text-4xl font-bold text-purple-600">
                      {formatCurrency(balanceInfo.balance)}
                    </p>
                  </div>

                  {/* Status Card */}
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <p className="text-sm text-gray-600 mb-2">Card Status</p>
                    <div className="flex items-center justify-between">
                      <div>
                        {getStatusBadge(balanceInfo.status)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Details */}
                <div className="mt-6 space-y-4">
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-gray-600">Card Number</span>
                    <span className="font-mono font-medium text-gray-900">{balanceInfo.card_number}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-gray-600">Expires</span>
                    <span className="font-medium text-gray-900">
                      {new Date(balanceInfo.expires_at).toLocaleDateString('en-NG', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-8 flex gap-4">
                  <Button variant="outline" className="flex-1" onClick={() => {
                    setCardNumber('');
                    setTenantId('');
                    setBalanceInfo(null);
                  }}>
                    Check Another Card
                  </Button>
                  <Link href="/gift-cards/transfer" className="flex-1">
                    <Button className="w-full">
                      Transfer Balance
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-base">Need Help?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <strong>Where's my card number?</strong> It's printed on the back of your physical gift card or included in your email receipt for digital cards.
            </p>
            <p>
              <strong>What if my card is expired?</strong> Expired cards cannot be used. Please contact the salon for assistance.
            </p>
            <p>
              <strong>Is my information secure?</strong> Yes! We use industry-standard encryption to protect your data. No login is required.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
