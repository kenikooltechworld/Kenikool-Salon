'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Send, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';
import { useGiftCardTransfer } from '@/lib/api/hooks/useGiftCards';

interface TransferFormData {
  sourceCard: string;
  destinationCard: string;
  amount: number;
  tenantId: string;
}

export default function TransferPage() {
  const [formData, setFormData] = useState<TransferFormData>({
    sourceCard: '',
    destinationCard: '',
    amount: 0,
    tenantId: '',
  });

  const { transfer, loading, error, data: transferResult } = useGiftCardTransfer();
  const [success, setSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Validation
      if (!formData.sourceCard.trim()) {
        throw new Error('Please enter source card number');
      }

      if (formData.amount <= 0) {
        throw new Error('Amount must be greater than 0');
      }

      if (!formData.tenantId.trim()) {
        throw new Error('Salon ID is required');
      }

      await transfer({
        tenantId: formData.tenantId,
        sourceCard: formData.sourceCard,
        destinationCard: formData.destinationCard || undefined,
        amount: formData.amount,
      });

      setSuccess(true);
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

  if (success && transferResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        {/* Header */}
        <div className="bg-white border-b">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Link href="/gift-cards" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4">
              <ArrowLeft className="w-4 h-4" />
              Back to Gift Cards
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Transfer Successful</h1>
          </div>
        </div>

        {/* Success Content */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="text-center">
                <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Transfer Complete!</h2>
                <p className="text-gray-600 mb-8">Your balance has been transferred successfully.</p>

                {/* Transfer Flow */}
                <div className="bg-white rounded-lg p-8 mb-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="text-center flex-1">
                      <p className="text-sm text-gray-600 mb-2">From</p>
                      <p className="font-mono font-semibold text-gray-900 text-sm">{transferResult.source_card}</p>
                    </div>
                    <ArrowRight className="w-6 h-6 text-purple-600 mx-4" />
                    <div className="text-center flex-1">
                      <p className="text-sm text-gray-600 mb-2">To</p>
                      <p className="font-mono font-semibold text-gray-900 text-sm">{transferResult.destination_card}</p>
                    </div>
                  </div>

                  <div className="border-t pt-6">
                    <p className="text-sm text-gray-600 mb-2">Amount Transferred</p>
                    <p className="text-3xl font-bold text-purple-600">{formatCurrency(transferResult.amount)}</p>
                  </div>
                </div>

                {/* Balances */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <p className="text-xs text-gray-600 mb-2">Source Card Balance</p>
                    <p className="text-lg font-bold text-gray-900">{formatCurrency(transferResult.source_balance)}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <p className="text-xs text-gray-600 mb-2">Destination Card Balance</p>
                    <p className="text-lg font-bold text-gray-900">{formatCurrency(transferResult.destination_balance)}</p>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <Link href="/gift-cards">
                    <Button variant="outline">
                      Back to Gift Cards
                    </Button>
                  </Link>
                  <Link href="/gift-cards/balance">
                    <Button>
                      Check Balance
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/gift-cards" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Gift Cards
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Transfer Balance</h1>
          <p className="text-gray-600 mt-2">Transfer balance from one gift card to another</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <CardHeader>
            <CardTitle>Transfer Gift Card Balance</CardTitle>
            <CardDescription>Move funds between gift cards or create a new card</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Salon ID */}
              <div>
                <label htmlFor="tenantId" className="block text-sm font-medium text-gray-700 mb-2">
                  Salon ID *
                </label>
                <Input
                  id="tenantId"
                  name="tenantId"
                  type="text"
                  placeholder="Enter salon ID"
                  value={formData.tenantId}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                />
              </div>

              {/* Source Card */}
              <div>
                <label htmlFor="sourceCard" className="block text-sm font-medium text-gray-700 mb-2">
                  Source Card Number *
                </label>
                <Input
                  id="sourceCard"
                  name="sourceCard"
                  type="text"
                  placeholder="e.g., GC-1234567890AB"
                  value={formData.sourceCard}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  The card you want to transfer balance FROM
                </p>
              </div>

              {/* Amount */}
              <div>
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                  Amount to Transfer (₦) *
                </label>
                <Input
                  id="amount"
                  name="amount"
                  type="number"
                  min="0"
                  step="100"
                  value={formData.amount || ''}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                  placeholder="0"
                />
              </div>

              {/* Destination Card */}
              <div>
                <label htmlFor="destinationCard" className="block text-sm font-medium text-gray-700 mb-2">
                  Destination Card Number
                </label>
                <Input
                  id="destinationCard"
                  name="destinationCard"
                  type="text"
                  placeholder="e.g., GC-9876543210XY (leave blank to create new)"
                  value={formData.destinationCard}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave blank to create a new card with the transferred balance
                </p>
              </div>

              {/* Info Alert */}
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Note:</strong> You can only transfer once per day per card. The transfer will be processed immediately.
                </AlertDescription>
              </Alert>

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
                    Processing Transfer...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Transfer Balance
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Info Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-base">How Transfers Work</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex gap-3">
              <div className="text-purple-600 font-bold">1</div>
              <div>
                <p className="font-medium text-gray-900">Enter Source Card</p>
                <p className="text-gray-600">The card you want to transfer balance FROM</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="text-purple-600 font-bold">2</div>
              <div>
                <p className="font-medium text-gray-900">Enter Amount</p>
                <p className="text-gray-600">How much you want to transfer</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="text-purple-600 font-bold">3</div>
              <div>
                <p className="font-medium text-gray-900">Choose Destination</p>
                <p className="text-gray-600">Enter an existing card or leave blank to create a new one</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="text-purple-600 font-bold">4</div>
              <div>
                <p className="font-medium text-gray-900">Confirm Transfer</p>
                <p className="text-gray-600">The balance will be transferred immediately</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
