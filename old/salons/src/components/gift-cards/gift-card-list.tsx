'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader, Eye } from 'lucide-react';

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

interface GiftCardListProps {
  cards: GiftCard[];
  loading: boolean;
  onCardClick: (card: GiftCard) => void;
}

export default function GiftCardList({
  cards,
  loading,
  onCardClick,
}: GiftCardListProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    const statusStyles: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-yellow-100 text-yellow-800',
      expired: 'bg-red-100 text-red-800',
      voided: 'bg-gray-100 text-gray-800',
    };

    return (
      <span
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
          statusStyles[status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getTypeBadge = (type: string) => {
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </span>
    );
  };

  const isExpiringSoon = (expiresAt: string) => {
    const expiryDate = new Date(expiresAt);
    const today = new Date();
    const daysUntilExpiry = Math.floor(
      (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-12 pb-12 flex items-center justify-center">
          <div className="text-center">
            <Loader className="w-8 h-8 text-purple-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading gift cards...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (cards.length === 0) {
    return (
      <Card>
        <CardContent className="pt-12 pb-12 text-center">
          <p className="text-gray-600">No gift cards found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Card Number
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Recipient
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Balance
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Type
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Status
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Expires
                </th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {cards.map((card) => (
                <tr
                  key={card.id}
                  className={`border-b hover:bg-gray-50 ${
                    isExpiringSoon(card.expires_at) ? 'bg-yellow-50' : ''
                  }`}
                >
                  <td className="py-3 px-4 font-mono text-sm text-gray-900">
                    {card.card_number}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {card.recipient_name || card.recipient_email || '-'}
                  </td>
                  <td className="py-3 px-4 font-semibold text-gray-900">
                    {formatCurrency(card.balance)}
                  </td>
                  <td className="py-3 px-4">{getTypeBadge(card.card_type)}</td>
                  <td className="py-3 px-4">{getStatusBadge(card.status)}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    <div>
                      {new Date(card.expires_at).toLocaleDateString('en-NG')}
                    </div>
                    {isExpiringSoon(card.expires_at) && (
                      <div className="text-xs text-orange-600 font-semibold">
                        Expiring soon
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCardClick(card)}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
