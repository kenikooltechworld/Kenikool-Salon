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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { PackagePurchase } from '@/lib/api/hooks/useClientPackages';

interface PackageTransferModalProps {
  package: PackagePurchase | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function PackageTransferModal({
  package: pkg,
  isOpen,
  onClose,
  onSuccess,
}: PackageTransferModalProps) {
  const [recipientEmail, setRecipientEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!pkg) return null;

  const totalCredits = pkg.credits.reduce((sum, c) => sum + c.remaining_quantity, 0);
  const canTransfer = totalCredits > 0 && pkg.status === 'active';

  const handleTransfer = async () => {
    if (!recipientEmail.trim()) {
      setError('Please enter a recipient email');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.post(`/packages/purchases/${pkg._id}/transfer`, {
        recipient_email: recipientEmail,
      });

      setSuccess(true);
      setTimeout(() => {
        setRecipientEmail('');
        setSuccess(false);
        onClose();
        onSuccess?.();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to transfer package');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Transfer Package</DialogTitle>
        </DialogHeader>

        {success ? (
          <div className="space-y-4 py-6">
            <div className="flex justify-center">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <p className="text-center text-gray-700">
              Package transferred successfully!
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

            {!canTransfer && (
              <Alert className="border-orange-200 bg-orange-50">
                <AlertCircle className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-orange-800">
                  {pkg.status !== 'active'
                    ? 'Only active packages can be transferred'
                    : 'No credits remaining to transfer'}
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
              <Label htmlFor="recipient-email">Recipient Email</Label>
              <Input
                id="recipient-email"
                type="email"
                placeholder="recipient@example.com"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                disabled={isLoading || !canTransfer}
              />
              <p className="text-xs text-gray-600">
                The recipient must have an account in the system
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Transfer Details</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Package</span>
                  <span className="font-medium">{pkg.package_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Credits</span>
                  <span className="font-medium">{totalCredits}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Expires</span>
                  <span className="font-medium">
                    {new Date(pkg.expiration_date).toLocaleDateString()}
                  </span>
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
              onClick={handleTransfer}
              disabled={isLoading || !canTransfer}
              className="gap-2"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Transfer
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
