'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { X, AlertCircle, CheckCircle } from 'lucide-react';
import { useGiftCardDashboard } from '@/lib/api/hooks/useGiftCardDashboard';

interface GiftCard {
  id: string;
  card_number: string;
  balance: number;
  status: string;
}

interface ReloadModalProps {
  card: GiftCard;
  tenantId: string;
  onClose: () => void;
}

export default function GiftCardReloadModal({
  card,
  tenantId,
  onClose,
}: ReloadModalProps) {
  const { reloadCard, loading, error } = useGiftCardDashboard();
  const [amount, setAmount] = useState<number>(0);
  const [success, setSuccess] = useState(false);

  const handleReload = async () => {
    if (amount <= 0) {
      return;
    }

    try {
      await reloadCard({
        tenantId,
        cardId: card.id,
        amount,
      });
      setSuccess(true);
      setTimeout(onClose, 2000);
    } catch (err) {
      // Error handled by hook
    }
  };

  if (success) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-12 pb-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Card Reloaded!
            </h2>
            <p className="text-gray-600">
              Gift card {card.card_number} has been reloaded with ₦{amount.toLocaleString()}.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Reload Gift Card</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Card Number</p>
            <p className="font-mono font-semibold text-gray-900">
              {card.card_number}
            </p>
            <p className="text-sm text-gray-600 mt-2">Current Balance</p>
            <p className="font-semibold text-gray-900">
              ₦{card.balance.toLocaleString()}
            </p>
          </div>

          <div>
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
              Reload Amount (₦) *
            </label>
            <Input
              id="amount"
              type="number"
              min="0"
              step="100"
              value={amount || ''}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              placeholder="Enter amount"
              disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">
              The expiration date will be extended by 1 year
            </p>
          </div>

          {amount > 0 && (
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm text-gray-600">New Balance</p>
              <p className="font-semibold text-blue-600">
                ₦{(card.balance + amount).toLocaleString()}
              </p>
            </div>
          )}

          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleReload}
              disabled={loading || amount <= 0}
              className="flex-1"
            >
              {loading ? 'Reloading...' : 'Reload'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
