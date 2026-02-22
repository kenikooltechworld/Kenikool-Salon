'use client';

import { useState } from 'react';
import { useRedeemRewards } from '@/lib/api/hooks/useReferrals';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Spinner } from '@/components/ui/spinner';
import { GiftIcon, AlertCircleIcon, CheckCircleIcon } from '@/components/icons';

interface RedeemRewardsModalProps {
  isOpen: boolean;
  onClose: () => void;
  clientId: string;
  availableBalance: number;
}

/**
 * Modal for redeeming earned referral rewards
 * Validates: REQ-4
 */
export function RedeemRewardsModal({
  isOpen,
  onClose,
  clientId,
  availableBalance,
}: RedeemRewardsModalProps) {
  const [amount, setAmount] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);
  const redeemMutation = useRedeemRewards();

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setAmount(value);
    setError('');
  };

  const validateAmount = (): boolean => {
    if (!amount || isNaN(Number(amount))) {
      setError('Please enter a valid amount');
      return false;
    }

    const numAmount = Number(amount);
    if (numAmount <= 0) {
      setError('Amount must be greater than 0');
      return false;
    }

    if (numAmount > availableBalance) {
      setError(`Insufficient balance. Available: ₦${availableBalance.toFixed(2)}`);
      return false;
    }

    return true;
  };

  const handleRedeem = async () => {
    if (!validateAmount()) return;

    try {
      await redeemMutation.mutateAsync({
        client_id: clientId,
        amount: Number(amount),
      });
      setSuccess(true);
      setAmount('');
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to redeem rewards'
      );
    }
  };

  const handleClose = () => {
    if (!redeemMutation.isPending) {
      setAmount('');
      setError('');
      setSuccess(false);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <GiftIcon size={20} className="text-blue-500" />
            </div>
            <div>
              <DialogTitle>Redeem Rewards</DialogTitle>
              <DialogDescription>
                Convert your earned rewards to account credit
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Available Balance */}
          <div className="bg-muted/50 rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">
              Available Balance
            </p>
            <p className="text-2xl font-bold">₦{availableBalance.toFixed(2)}</p>
          </div>

          {/* Success Message */}
          {success && (
            <Alert className="bg-green-500/10 border-green-500/20">
              <CheckCircleIcon className="h-4 w-4 text-green-500" />
              <AlertDescription className="text-green-700">
                Rewards redeemed successfully!
              </AlertDescription>
            </Alert>
          )}

          {/* Error Message */}
          {error && (
            <Alert className="bg-red-500/10 border-red-500/20">
              <AlertCircleIcon className="h-4 w-4 text-red-500" />
              <AlertDescription className="text-red-700">{error}</AlertDescription>
            </Alert>
          )}

          {/* Amount Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Redemption Amount</label>
            <div className="flex items-center gap-2">
              <span className="text-lg font-semibold">₦</span>
              <Input
                type="number"
                placeholder="Enter amount"
                value={amount}
                onChange={handleAmountChange}
                disabled={redeemMutation.isPending}
                min="0"
                step="100"
                className="flex-1"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Maximum: ₦{availableBalance.toFixed(2)}
            </p>
          </div>

          {/* Quick Amount Buttons */}
          <div className="grid grid-cols-3 gap-2">
            {[25, 50, 100].map((percent) => {
              const quickAmount = (availableBalance * percent) / 100;
              return (
                <Button
                  key={percent}
                  variant="outline"
                  size="sm"
                  onClick={() => setAmount(quickAmount.toString())}
                  disabled={redeemMutation.isPending}
                >
                  {percent}%
                </Button>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={redeemMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleRedeem}
              disabled={redeemMutation.isPending || !amount}
              className="flex-1"
            >
              {redeemMutation.isPending ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Processing...
                </>
              ) : (
                'Redeem'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
