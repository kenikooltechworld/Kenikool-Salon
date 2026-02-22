'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { PackagePurchase } from '@/lib/api/hooks/useClientPackages';

interface PackageRefundModalProps {
  package: PackagePurchase | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function PackageRefundModal({
  package: pkg,
  isOpen,
  onClose,
  onSuccess,
}: PackageRefundModalProps) {
  const [reason, setReason] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!pkg) return null;

  const totalCredits = pkg.credits.reduce((sum, c) => sum + c.remaining_quantity, 0);
  const totalInitialCredits = pkg.credits.reduce((sum, c) => sum + c.initial_quantity, 0);
  const refundAmount = totalCredits > 0 
    ? (totalCredits / totalInitialCredits) * pkg.amount_paid 
    : 0;
  const canRefund = pkg.status === 'active' && totalCredits > 0;

  const handleRefund = async () => {
    if (!reason.trim()) {
      setError('Please provide a reason for the refund');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.post(`/packages/purchases/${pkg._id}/refund`, {
        reason,
      });

      setSuccess(true);
      setTimeout(() => {
        setReason('');
        setSuccess(false);
        onClose();
        onSuccess?.();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process refund');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Refund Package</DialogTitle>
        </DialogHeader>

        {success ? (
          <div className="space-y-4 py-6">
            <div className="flex justify-center">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <p className="text-center text-gray-700">
              Refund processed successfully!
            </p>
            <p className="text-center text-sm text-gray-600">
              ${refundAmount.toFixed(2)} has been refunded
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-900">
                <span className="font-semibold">{pkg.package_name}</span>
                <br />
                <span className="text-blue-800">
                  {totalCredits} credit{totalCredits !== 1 ? 's' : ''} remaining
                </span>
              </p>
            </div>

            {!canRefund && (
              <Alert className="border-orange-200 bg-orange-50">
                <AlertCircle className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-orange-800">
                  {pkg.status !== 'active'
                    ? 'Only active packages can be refunded'
                    : 'No credits remaining to refund'}
                </AlertDescription>
              </Alert>
            )}

            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Refund Amount</p>
              <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                <p className="text-2xl font-bold text-gray-900">
                  ${refundAmount.toFixed(2)}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Based on {totalCredits} remaining credit{totalCredits !== 1 ? 's' : ''} out of {totalInitialCredits}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="reason">Reason for Refund</Label>
              <Textarea
                id="reason"
                placeholder="Please explain why you're requesting a refund..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                disabled={isLoading || !canRefund}
                className="min-h-24"
              />
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Refund Details</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Original Price</span>
                  <span className="font-medium">${pkg.amount_paid.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Refund Amount</span>
                  <span className="font-medium text-green-600">${refundAmount.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {!success && (
          <DialogFooter>
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRefund}
              disabled={isLoading || !canRefund}
              className="gap-2"
              variant="destructive"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Process Refund
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
