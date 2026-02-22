'use client';

import { useState, useEffect } from 'react';
import {
  useUpdatePaymentMethod,
  MembershipSubscription,
} from '@/lib/api/hooks/useMemberships';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { showToast } from '@/lib/utils/toast';
import { CreditCardIcon, LockIcon } from '@/components/icons';
import { loadPaystackScript } from '@/lib/utils/paystack';

// Extend Window interface for Paystack
declare global {
  interface Window {
    PaystackPop: any;
  }
}

interface PaymentMethodModalProps {
  isOpen: boolean;
  onClose: () => void;
  subscription: MembershipSubscription;
  onSuccess?: () => void;
}

export function PaymentMethodModal({
  isOpen,
  onClose,
  subscription,
  onSuccess,
}: PaymentMethodModalProps) {
  const updateMutation = useUpdatePaymentMethod();

  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);

  // Load Paystack script on component mount
  useEffect(() => {
    if (isOpen) {
      loadPaystackScript().catch((error) => {
        console.error('Failed to load Paystack script:', error);
      });
    }
  }, [isOpen]);

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];

    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
      return parts.join(' ');
    } else {
      return value;
    }
  };

  const formatExpiryDate = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.slice(0, 2) + '/' + v.slice(2, 4);
    }
    return v;
  };

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCardNumber(formatCardNumber(e.target.value));
  };

  const handleExpiryDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setExpiryDate(formatExpiryDate(e.target.value));
  };

  const handleCVVChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/gi, '').slice(0, 4);
    setCvv(value);
  };

  const validateForm = () => {
    if (!cardNumber.replace(/\s/g, '')) {
      showToast('Please enter a card number', 'error');
      return false;
    }

    if (cardNumber.replace(/\s/g, '').length < 13) {
      showToast('Card number must be at least 13 digits', 'error');
      return false;
    }

    if (!expiryDate) {
      showToast('Please enter expiry date', 'error');
      return false;
    }

    if (!cvv) {
      showToast('Please enter CVV', 'error');
      return false;
    }

    if (!cardholderName) {
      showToast('Please enter cardholder name', 'error');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      // In a real implementation, this would tokenize the card with Paystack
      // For now, we'll use a placeholder authorization code
      const authCode = `auth_${Date.now()}`;

      await updateMutation.mutateAsync({
        subscriptionId: subscription._id,
        paymentMethodId: authCode,
      });

      showToast('Payment method updated successfully', 'success');
      setCardNumber('');
      setExpiryDate('');
      setCvv('');
      setCardholderName('');
      setShowConfirm(false);
      onClose();
      onSuccess?.();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to update payment method',
        'error'
      );
    }
  };

  const maskedCardNumber = cardNumber
    ? `•••• •••• •••• ${cardNumber.slice(-4)}`
    : 'Not set';

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Update Payment Method</h2>
          <p className="text-muted-foreground mt-1">
            Update the payment method for this subscription
          </p>
        </div>

        {/* Current Payment Method */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Current Payment Method</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <CreditCardIcon size={24} className="text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Card Number</p>
                <p className="font-mono font-medium">{maskedCardNumber}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {!showConfirm ? (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-md flex items-start gap-3">
              <LockIcon size={20} className="text-blue-600 mt-0.5 shrink-0" />
              <p className="text-sm text-blue-700">
                Your payment information is secure and encrypted. We never store
                your full card details.
              </p>
            </div>

            <Button
              onClick={() => setShowConfirm(true)}
              className="w-full"
              disabled={updateMutation.isPending}
            >
              Update Payment Method
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Cardholder Name */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Cardholder Name</label>
              <Input
                placeholder="John Doe"
                value={cardholderName}
                onChange={(e) => setCardholderName(e.target.value)}
                disabled={updateMutation.isPending}
              />
            </div>

            {/* Card Number */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Card Number</label>
              <Input
                placeholder="1234 5678 9012 3456"
                value={cardNumber}
                onChange={handleCardNumberChange}
                maxLength={19}
                disabled={updateMutation.isPending}
              />
            </div>

            {/* Expiry Date and CVV */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Expiry Date</label>
                <Input
                  placeholder="MM/YY"
                  value={expiryDate}
                  onChange={handleExpiryDateChange}
                  maxLength={5}
                  disabled={updateMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">CVV</label>
                <Input
                  placeholder="123"
                  value={cvv}
                  onChange={handleCVVChange}
                  maxLength={4}
                  type="password"
                  disabled={updateMutation.isPending}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-4 border-t border-border">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowConfirm(false);
                  setCardNumber('');
                  setExpiryDate('');
                  setCvv('');
                  setCardholderName('');
                }}
                disabled={updateMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Updating...' : 'Update Payment Method'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
}
