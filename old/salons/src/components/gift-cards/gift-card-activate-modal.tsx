'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { X, AlertCircle, CheckCircle } from 'lucide-react';
import { useGiftCardDashboard } from '@/lib/api/hooks/useGiftCardDashboard';

interface GiftCard {
  id: string;
  card_number: string;
  balance: number;
  status: string;
}

interface ActivateModalProps {
  card: GiftCard;
  tenantId: string;
  onClose: () => void;
}

export default function GiftCardActivateModal({
  card,
  tenantId,
  onClose,
}: ActivateModalProps) {
  const { activateCard, loading, error } = useGiftCardDashboard();
  const [success, setSuccess] = useState(false);

  const handleActivate = async () => {
    try {
      await activateCard({
        tenantId,
        cardId: card.id,
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
              Card Activated!
            </h2>
            <p className="text-gray-600">
              Gift card {card.card_number} has been activated successfully.
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
          <CardTitle>Activate Gift Card</CardTitle>
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
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              This will activate the gift card and make it available for use.
            </AlertDescription>
          </Alert>

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
              onClick={handleActivate}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Activating...' : 'Activate'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
