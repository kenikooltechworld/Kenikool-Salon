'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useRefundPayment } from '@/lib/api/hooks/useRefundPayment';
import { Payment, RefundRequest } from '@/lib/api/types';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';

interface RefundModalProps {
  payment: Payment | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * Refund Modal Component
 * Allows users to process full or partial refunds with validation
 * Validates: Requirements 2.1, 2.2, 2.3, 2.7
 */
export function RefundModal({
  payment,
  isOpen,
  onClose,
  onSuccess,
}: RefundModalProps) {
  const [refundAmount, setRefundAmount] = useState<string>('');
  const [refundType, setRefundType] = useState<'full' | 'partial'>('full');
  const [reason, setReason] = useState('');
  const [step, setStep] = useState<'form' | 'confirm' | 'processing' | 'success' | 'error'>(
    'form'
  );
  const [errorMessage, setErrorMessage] = useState('');

  const { mutate: processRefund, isPending } = useRefundPayment();

  if (!isOpen || !payment) return null;

  const maxRefundAmount = payment.amount - (payment.refund_amount || 0);
  const currentRefundAmount = parseFloat(refundAmount) || 0;
  const isValidAmount =
    currentRefundAmount > 0 && currentRefundAmount <= maxRefundAmount;

  const handleRefundTypeChange = (type: 'full' | 'partial') => {
    setRefundType(type);
    if (type === 'full') {
      setRefundAmount(maxRefundAmount.toString());
    } else {
      setRefundAmount('');
    }
  };

  const handleSubmit = () => {
    if (!isValidAmount) {
      setErrorMessage('Invalid refund amount');
      return;
    }
    if (!reason.trim()) {
      setErrorMessage('Refund reason is required');
      return;
    }
    setStep('confirm');
  };

  const handleConfirm = () => {
    setStep('processing');
    setErrorMessage('');

    const refundData: RefundRequest = {
      payment_id: payment.id,
      refund_amount: currentRefundAmount,
      reason: reason.trim(),
      refund_type: refundType,
    };

    processRefund(refundData, {
      onSuccess: () => {
        setStep('success');
        setTimeout(() => {
          onSuccess?.();
          handleClose();
        }, 2000);
      },
      onError: (error: any) => {
        setStep('error');
        setErrorMessage(
          error.response?.data?.message || 'Failed to process refund'
        );
      },
    });
  };

  const handleClose = () => {
    setStep('form');
    setRefundAmount('');
    setRefundType('full');
    setReason('');
    setErrorMessage('');
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Process Refund</DialogTitle>
          <DialogClose />
        </DialogHeader>

        {/* Form Step */}
        {step === 'form' && (
          <div className="space-y-4">
            <div>
              <Label className="text-sm font-medium">Payment Reference</Label>
              <p className="text-lg font-semibold">{payment.reference}</p>
            </div>

            <div>
              <Label className="text-sm font-medium">Original Amount</Label>
              <p className="text-lg font-semibold">
                ₦{payment.amount.toLocaleString()}
              </p>
            </div>

            {payment.refund_amount && (
              <div>
                <Label className="text-sm font-medium">Already Refunded</Label>
                <p className="text-lg font-semibold text-orange-600">
                  ₦{payment.refund_amount.toLocaleString()}
                </p>
              </div>
            )}

            <div>
              <Label className="text-sm font-medium">Max Refundable Amount</Label>
              <p className="text-lg font-semibold text-green-600">
                ₦{maxRefundAmount.toLocaleString()}
              </p>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Refund Type</Label>
              <div className="flex gap-2">
                <Button
                  variant={refundType === 'full' ? 'primary' : 'outline'}
                  onClick={() => handleRefundTypeChange('full')}
                  className="flex-1"
                >
                  Full Refund
                </Button>
                <Button
                  variant={refundType === 'partial' ? 'primary' : 'outline'}
                  onClick={() => handleRefundTypeChange('partial')}
                  className="flex-1"
                >
                  Partial Refund
                </Button>
              </div>
            </div>

            {refundType === 'partial' && (
              <div>
                <Label htmlFor="refund-amount" className="text-sm font-medium">
                  Refund Amount
                </Label>
                <Input
                  id="refund-amount"
                  type="number"
                  min="0"
                  max={maxRefundAmount}
                  step="0.01"
                  value={refundAmount}
                  onChange={(e) => setRefundAmount(e.target.value)}
                  placeholder="Enter amount"
                  className="mt-1"
                />
                {refundAmount && !isValidAmount && (
                  <p className="text-xs text-red-600 mt-1">
                    Amount must be between 0 and ₦{maxRefundAmount.toLocaleString()}
                  </p>
                )}
              </div>
            )}

            <div>
              <Label htmlFor="reason" className="text-sm font-medium">
                Refund Reason
              </Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Enter reason for refund"
                className="mt-1 min-h-24"
              />
            </div>

            {errorMessage && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex gap-2 text-sm text-red-700">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSubmit}
                disabled={!isValidAmount || !reason.trim()}
                className="flex-1"
              >
                Continue
              </Button>
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Confirmation Step */}
        {step === 'confirm' && (
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-2">
                Confirm Refund
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Refund Amount:</span>
                  <span className="font-semibold">
                    ₦{currentRefundAmount.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-semibold capitalize">{refundType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Reason:</span>
                  <span className="font-semibold">{reason}</span>
                </div>
              </div>
            </div>

            <p className="text-sm text-gray-600">
              This action cannot be undone. The customer will be refunded
              ₦{currentRefundAmount.toLocaleString()} to their original payment
              method.
            </p>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleConfirm}
                disabled={isPending}
                className="flex-1"
              >
                {isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Confirm Refund
              </Button>
              <Button
                variant="outline"
                onClick={() => setStep('form')}
                disabled={isPending}
                className="flex-1"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <p className="text-center text-gray-600">Processing refund...</p>
          </div>
        )}

        {/* Success Step */}
        {step === 'success' && (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <p className="text-center font-semibold text-green-600">
              Refund processed successfully!
            </p>
            <p className="text-center text-sm text-gray-600">
              ₦{currentRefundAmount.toLocaleString()} has been refunded to the
              customer.
            </p>
          </div>
        )}

        {/* Error Step */}
        {step === 'error' && (
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900">Refund Failed</h4>
                <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep('form')}
                className="flex-1"
              >
                Try Again
              </Button>
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Close
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
