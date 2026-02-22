'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { X, AlertCircle, CheckCircle } from 'lucide-react';
import { useGiftCardDashboard } from '@/lib/api/hooks/useGiftCardDashboard';
import GiftCardActivateModal from './gift-card-activate-modal';
import GiftCardVoidModal from './gift-card-void-modal';
import GiftCardReloadModal from './gift-card-reload-modal';
import GiftCardResendModal from './gift-card-resend-modal';

interface GiftCard {
  id: string;
  card_number: string;
  balance: number;
  status: string;
  card_type: 'digital' | 'physical';
  created_at: string;
  expires_at: string;
  recipient_email?: string;
  recipient_name?: string;
}

interface DetailModalProps {
  card: GiftCard;
  tenantId: string;
  onClose: () => void;
}

export default function GiftCardDetailModal({
  card,
  tenantId,
  onClose,
}: DetailModalProps) {
  const [showActivateModal, setShowActivateModal] = useState(false);
  const [showVoidModal, setShowVoidModal] = useState(false);
  const [showReloadModal, setShowReloadModal] = useState(false);
  const [showResendModal, setShowResendModal] = useState(false);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'text-green-600',
      inactive: 'text-yellow-600',
      expired: 'text-red-600',
      voided: 'text-gray-600',
    };
    return colors[status] || 'text-gray-600';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Gift Card Details</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
          >
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Card Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Card Number</p>
              <p className="font-mono font-semibold text-gray-900">{card.card_number}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Balance</p>
              <p className="text-lg font-bold text-purple-600">
                {formatCurrency(card.balance)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-semibold ${getStatusColor(card.status)}`}>
                {card.status.charAt(0).toUpperCase() + card.status.slice(1)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Type</p>
              <p className="font-semibold text-gray-900">
                {card.card_type.charAt(0).toUpperCase() + card.card_type.slice(1)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Created</p>
              <p className="text-sm text-gray-900">
                {new Date(card.created_at).toLocaleDateString('en-NG')}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Expires</p>
              <p className="text-sm text-gray-900">
                {new Date(card.expires_at).toLocaleDateString('en-NG')}
              </p>
            </div>
          </div>

          {/* Recipient Info */}
          {card.recipient_name && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-600">Recipient Name</p>
              <p className="font-semibold text-gray-900">{card.recipient_name}</p>
            </div>
          )}

          {card.recipient_email && (
            <div>
              <p className="text-sm text-gray-600">Recipient Email</p>
              <p className="font-semibold text-gray-900">{card.recipient_email}</p>
            </div>
          )}

          {/* Actions */}
          <div className="border-t pt-6">
            <p className="text-sm font-semibold text-gray-900 mb-4">Actions</p>
            <div className="grid grid-cols-2 gap-3">
              {card.status === 'inactive' && (
                <Button
                  onClick={() => setShowActivateModal(true)}
                  className="w-full"
                >
                  Activate
                </Button>
              )}

              {card.status !== 'voided' && (
                <Button
                  variant="destructive"
                  onClick={() => setShowVoidModal(true)}
                  className="w-full"
                >
                  Void
                </Button>
              )}

              {card.status === 'active' && (
                <Button
                  variant="outline"
                  onClick={() => setShowReloadModal(true)}
                  className="w-full"
                >
                  Reload
                </Button>
              )}

              {card.card_type === 'digital' && (
                <Button
                  variant="outline"
                  onClick={() => setShowResendModal(true)}
                  className="w-full"
                >
                  Resend
                </Button>
              )}
            </div>
          </div>

          {/* Close Button */}
          <Button variant="outline" onClick={onClose} className="w-full">
            Close
          </Button>
        </CardContent>
      </Card>

      {/* Sub-modals */}
      {showActivateModal && (
        <GiftCardActivateModal
          card={card}
          tenantId={tenantId}
          onClose={() => {
            setShowActivateModal(false);
            onClose();
          }}
        />
      )}

      {showVoidModal && (
        <GiftCardVoidModal
          card={card}
          tenantId={tenantId}
          onClose={() => {
            setShowVoidModal(false);
            onClose();
          }}
        />
      )}

      {showReloadModal && (
        <GiftCardReloadModal
          card={card}
          tenantId={tenantId}
          onClose={() => {
            setShowReloadModal(false);
            onClose();
          }}
        />
      )}

      {showResendModal && (
        <GiftCardResendModal
          card={card}
          tenantId={tenantId}
          onClose={() => {
            setShowResendModal(false);
            onClose();
          }}
        />
      )}
    </div>
  );
}
