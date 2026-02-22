'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Gift, AlertCircle, CheckCircle } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { useGiftCardPurchase } from '@/lib/api/hooks/useGiftCards';

interface PurchaseFormData {
  amount: number;
  cardType: 'digital' | 'physical';
  recipientName: string;
  recipientEmail: string;
  message: string;
  designTheme: string;
  tenantId: string;
}

export default function PurchasePage() {
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState<PurchaseFormData>({
    amount: 5000,
    cardType: 'digital',
    recipientName: '',
    recipientEmail: '',
    message: '',
    designTheme: 'default',
    tenantId: searchParams.get('tenant') || '',
  });

  const { purchase, loading, error, data: purchaseResult } = useGiftCardPurchase();
  const [success, setSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value
    }));
  };

  const handleCardTypeChange = (type: 'digital' | 'physical') => {
    setFormData(prev => ({
      ...prev,
      cardType: type
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Validation
      if (formData.amount < 1000 || formData.amount > 500000) {
        throw new Error('Amount must be between ₦1,000 and ₦500,000');
      }

      if (formData.cardType === 'digital' && !formData.recipientEmail) {
        throw new Error('Email is required for digital gift cards');
      }

      if (!formData.tenantId) {
        throw new Error('Salon ID is required');
      }

      await purchase({
        tenantId: formData.tenantId,
        amount: formData.amount,
        cardType: formData.cardType,
        recipientName: formData.recipientName || undefined,
        recipientEmail: formData.recipientEmail || undefined,
        message: formData.message || undefined,
        designTheme: formData.designTheme,
        paymentMethod: 'paystack',
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

  const presetAmounts = [1000, 5000, 10000, 25000, 50000, 100000];

  if (success && purchaseResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        {/* Header */}
        <div className="bg-white border-b">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Link href="/gift-cards" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4">
              <ArrowLeft className="w-4 h-4" />
              Back to Gift Cards
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Purchase Successful</h1>
          </div>
        </div>

        {/* Success Content */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="text-center">
                <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Gift Card Created!</h2>
                <p className="text-gray-600 mb-6">Your gift card has been created successfully.</p>

                <div className="bg-white rounded-lg p-6 mb-6 text-left space-y-4">
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-gray-600">Card Number</span>
                    <span className="font-mono font-medium text-gray-900">{purchaseResult.card_number}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-gray-600">Amount</span>
                    <span className="font-medium text-gray-900">{formatCurrency(purchaseResult.amount)}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-gray-600">Type</span>
                    <span className="font-medium text-gray-900 capitalize">{purchaseResult.card_type}</span>
                  </div>
                  {purchaseResult.recipient_email && (
                    <div className="flex justify-between items-center py-3">
                      <span className="text-gray-600">Recipient Email</span>
                      <span className="font-medium text-gray-900">{purchaseResult.recipient_email}</span>
                    </div>
                  )}
                </div>

                <Alert className="mb-6 bg-blue-50 border-blue-200">
                  <AlertCircle className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    {purchaseResult.card_type === 'digital'
                      ? 'Your digital gift card will be sent to the recipient email shortly.'
                      : 'Your physical gift card will be ready for pickup or delivery.'}
                  </AlertDescription>
                </Alert>

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
          <h1 className="text-3xl font-bold text-gray-900">Purchase Gift Card</h1>
          <p className="text-gray-600 mt-2">Create a gift card for yourself or someone special</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Gift Card Details</CardTitle>
                <CardDescription>Fill in the details for your gift card</CardDescription>
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

                  {/* Card Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Card Type *
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <button
                        type="button"
                        onClick={() => handleCardTypeChange('digital')}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          formData.cardType === 'digital'
                            ? 'border-purple-600 bg-purple-50'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                      >
                        <Gift className="w-6 h-6 mx-auto mb-2" />
                        <p className="font-medium text-gray-900">Digital</p>
                        <p className="text-xs text-gray-600">Sent via email</p>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleCardTypeChange('physical')}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          formData.cardType === 'physical'
                            ? 'border-purple-600 bg-purple-50'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                      >
                        <Gift className="w-6 h-6 mx-auto mb-2" />
                        <p className="font-medium text-gray-900">Physical</p>
                        <p className="text-xs text-gray-600">Pickup or mail</p>
                      </button>
                    </div>
                  </div>

                  {/* Amount */}
                  <div>
                    <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                      Amount (₦) *
                    </label>
                    <Input
                      id="amount"
                      name="amount"
                      type="number"
                      min="1000"
                      max="500000"
                      step="100"
                      value={formData.amount}
                      onChange={handleInputChange}
                      disabled={loading}
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Between ₦1,000 and ₦500,000
                    </p>

                    {/* Preset Amounts */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {presetAmounts.map(amount => (
                        <button
                          key={amount}
                          type="button"
                          onClick={() => setFormData(prev => ({ ...prev, amount }))}
                          className="px-3 py-1 text-sm rounded-full bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
                        >
                          {formatCurrency(amount)}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Recipient Name */}
                  <div>
                    <label htmlFor="recipientName" className="block text-sm font-medium text-gray-700 mb-2">
                      Recipient Name
                    </label>
                    <Input
                      id="recipientName"
                      name="recipientName"
                      type="text"
                      placeholder="Leave blank if for yourself"
                      value={formData.recipientName}
                      onChange={handleInputChange}
                      disabled={loading}
                    />
                  </div>

                  {/* Recipient Email */}
                  {formData.cardType === 'digital' && (
                    <div>
                      <label htmlFor="recipientEmail" className="block text-sm font-medium text-gray-700 mb-2">
                        Recipient Email *
                      </label>
                      <Input
                        id="recipientEmail"
                        name="recipientEmail"
                        type="email"
                        placeholder="recipient@example.com"
                        value={formData.recipientEmail}
                        onChange={handleInputChange}
                        disabled={loading}
                        required={formData.cardType === 'digital'}
                      />
                    </div>
                  )}

                  {/* Message */}
                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                      Personal Message
                    </label>
                    <Textarea
                      id="message"
                      name="message"
                      placeholder="Add a special message (optional)"
                      value={formData.message}
                      onChange={handleInputChange}
                      disabled={loading}
                      rows={3}
                    />
                  </div>

                  {/* Design Theme */}
                  <div>
                    <label htmlFor="designTheme" className="block text-sm font-medium text-gray-700 mb-2">
                      Design Theme
                    </label>
                    <select
                      id="designTheme"
                      name="designTheme"
                      value={formData.designTheme}
                      onChange={handleInputChange}
                      disabled={loading}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    >
                      <option value="default">Default</option>
                      <option value="birthday">Birthday</option>
                      <option value="christmas">Christmas</option>
                      <option value="valentine">Valentine</option>
                    </select>
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
                        Creating Gift Card...
                      </>
                    ) : (
                      <>
                        <Gift className="w-4 h-4 mr-2" />
                        Create Gift Card
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Summary */}
          <div>
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle className="text-base">Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-gray-600">Amount</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(formData.amount)}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-gray-600">Type</span>
                  <span className="font-semibold text-gray-900 capitalize">{formData.cardType}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-gray-600">Processing Fee</span>
                  <span className="font-semibold text-gray-900">Free</span>
                </div>
                <div className="flex justify-between items-center py-3 bg-purple-50 px-3 rounded-lg">
                  <span className="font-semibold text-gray-900">Total</span>
                  <span className="font-bold text-purple-600 text-lg">{formatCurrency(formData.amount)}</span>
                </div>

                <Alert className="mt-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-xs">
                    You'll be redirected to payment after clicking "Create Gift Card"
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
