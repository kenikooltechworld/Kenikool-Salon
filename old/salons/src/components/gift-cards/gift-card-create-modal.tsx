'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { X, AlertCircle, CheckCircle, Gift } from 'lucide-react';
import { useGiftCardPurchase } from '@/lib/api/hooks/useGiftCards';

interface CreateModalProps {
  tenantId: string;
  onClose: () => void;
}

export default function GiftCardCreateModal({
  tenantId,
  onClose,
}: CreateModalProps) {
  const { purchase, loading, error } = useGiftCardPurchase();
  const [success, setSuccess] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [formData, setFormData] = useState({
    amount: 5000,
    cardType: 'digital' as 'digital' | 'physical',
    recipientName: '',
    recipientEmail: '',
    message: '',
    designTheme: 'default',
  });

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value,
    }));
  };

  const handleCreate = async () => {
    try {
      if (formData.amount < 1000 || formData.amount > 500000) {
        return;
      }

      if (formData.cardType === 'digital' && !formData.recipientEmail) {
        return;
      }

      const res = await purchase({
        tenantId,
        amount: formData.amount,
        cardType: formData.cardType,
        recipientName: formData.recipientName || undefined,
        recipientEmail: formData.recipientEmail || undefined,
        message: formData.message || undefined,
        designTheme: formData.designTheme,
        paymentMethod: 'manual',
      });

      setResult(res);
      setSuccess(true);
      setTimeout(onClose, 3000);
    } catch (err) {
      // Error handled by hook
    }
  };

  if (success && result) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-12 pb-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Gift Card Created!
            </h2>
            <p className="text-gray-600 mb-4">
              Card {result.card_number} has been created successfully.
            </p>
            <div className="bg-gray-50 p-3 rounded-lg text-left">
              <p className="text-xs text-gray-600">Card Number</p>
              <p className="font-mono font-semibold text-gray-900 text-sm">
                {result.card_number}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <Card className="w-full max-w-md mx-4 my-8">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Create Gift Card</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-4 max-h-96 overflow-y-auto">
          {/* Card Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Card Type *
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(['digital', 'physical'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setFormData((prev) => ({ ...prev, cardType: type }))}
                  className={`p-3 rounded-lg border-2 transition-all text-sm ${
                    formData.cardType === type
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <Gift className="w-4 h-4 mx-auto mb-1" />
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
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
            />
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
              value={formData.recipientName}
              onChange={handleInputChange}
              placeholder="Optional"
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
                value={formData.recipientEmail}
                onChange={handleInputChange}
                placeholder="recipient@example.com"
                disabled={loading}
                required
              />
            </div>
          )}

          {/* Message */}
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
              Message
            </label>
            <Textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              placeholder="Optional message"
              disabled={loading}
              rows={2}
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

          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={
                loading ||
                formData.amount < 1000 ||
                formData.amount > 500000 ||
                (formData.cardType === 'digital' && !formData.recipientEmail)
              }
              className="flex-1"
            >
              {loading ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
