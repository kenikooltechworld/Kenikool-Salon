import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useGetGiftCardBalance,
  useRedeemGiftCard,
} from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { Loader2 } from "@/components/icons";

interface GiftCardRedeemModalProps {
  open: boolean;
  onClose: () => void;
  transactionId: string;
  onRedeemed: (amount: number) => void;
}

export function GiftCardRedeemModal({
  open,
  onClose,
  transactionId,
  onRedeemed,
}: GiftCardRedeemModalProps) {
  const [cardNumber, setCardNumber] = useState("");
  const [amount, setAmount] = useState("");
  const [balance, setBalance] = useState<number | null>(null);

  const getBalance = useGetGiftCardBalance();
  const redeemCard = useRedeemGiftCard();

  const handleCheckBalance = async () => {
    if (!cardNumber) {
      toast.error("Please enter card number");
      return;
    }

    try {
      const result = await getBalance.mutateAsync(cardNumber);
      setBalance(result.balance);
      toast.success(`Balance: ${formatCurrency(result.balance)}`);
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to check balance");
      setBalance(null);
    }
  };

  const handleRedeem = async () => {
    if (!cardNumber || !amount) {
      toast.error("Please enter card number and amount");
      return;
    }

    const redeemAmount = parseFloat(amount);
    if (isNaN(redeemAmount) || redeemAmount <= 0) {
      toast.error("Invalid amount");
      return;
    }

    if (balance !== null && redeemAmount > balance) {
      toast.error("Amount exceeds card balance");
      return;
    }

    try {
      await redeemCard.mutateAsync({
        card_number: cardNumber,
        amount: redeemAmount,
        transaction_id: transactionId,
      });

      toast.success(`Redeemed ${formatCurrency(redeemAmount)}`);
      onRedeemed(redeemAmount);
      handleClose();
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to redeem gift card");
    }
  };

  const handleClose = () => {
    setCardNumber("");
    setAmount("");
    setBalance(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Redeem Gift Card</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label htmlFor="cardNumber">Gift Card Number</Label>
            <div className="flex gap-2">
              <Input
                id="cardNumber"
                value={cardNumber}
                onChange={(e) => setCardNumber(e.target.value.toUpperCase())}
                placeholder="GC-XXXXXXXXXXXX"
              />
              <Button
                onClick={handleCheckBalance}
                disabled={getBalance.isPending}
                variant="outline"
              >
                {getBalance.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Check"
                )}
              </Button>
            </div>
          </div>

          {balance !== null && (
            <div className="p-3 bg-muted rounded-md">
              <p className="text-sm font-medium">
                Available Balance: {formatCurrency(balance)}
              </p>
            </div>
          )}

          <div>
            <Label htmlFor="amount">Amount to Redeem</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              onClick={handleRedeem}
              disabled={redeemCard.isPending || !balance}
            >
              {redeemCard.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Redeeming...
                </>
              ) : (
                "Redeem"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
