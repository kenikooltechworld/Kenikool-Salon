import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRefundTransaction, POSTransaction } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { AlertCircleIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface RefundModalProps {
  transaction: POSTransaction | null;
  open: boolean;
  onClose: () => void;
}

const REFUND_REASONS = [
  "Customer Request",
  "Wrong Item",
  "Defective Product",
  "Service Issue",
  "Pricing Error",
  "Other",
];

export function RefundModal({ transaction, open, onClose }: RefundModalProps) {
  const [refundAmount, setRefundAmount] = useState("");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [isFullRefund, setIsFullRefund] = useState(true);

  const refundTransaction = useRefundTransaction();

  const handleClose = () => {
    setRefundAmount("");
    setReason("");
    setNotes("");
    setIsFullRefund(true);
    onClose();
  };

  const handleRefund = async () => {
    if (!transaction) return;

    // Validate inputs
    if (!reason) {
      toast.error("Please select a refund reason");
      return;
    }

    const amount = isFullRefund ? transaction.total : parseFloat(refundAmount);

    if (!isFullRefund && (!refundAmount || amount <= 0)) {
      toast.error("Please enter a valid refund amount");
      return;
    }

    if (amount > transaction.total) {
      toast.error("Refund amount cannot exceed transaction total");
      return;
    }

    try {
      await refundTransaction.mutateAsync({
        transaction_id: transaction.id,
        refund_amount: amount,
        reason: notes ? `${reason}: ${notes}` : reason,
      });

      toast.success(
        `Transaction refunded successfully: ${formatCurrency(amount)}`
      );
      handleClose();
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "Failed to refund transaction"
      );
    }
  };

  if (!transaction) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Refund Transaction</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Warning */}
          <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <AlertCircleIcon className="h-5 w-5 text-destructive mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-destructive">Warning</p>
              <p className="text-muted-foreground">
                This action cannot be undone. The refund will be processed
                immediately.
              </p>
            </div>
          </div>

          {/* Transaction Info */}
          <div className="p-3 bg-muted rounded-lg space-y-1">
            <p className="text-sm text-muted-foreground">Transaction</p>
            <p className="font-medium">{transaction.transaction_number}</p>
            <p className="text-lg font-bold">
              {formatCurrency(transaction.total)}
            </p>
          </div>

          {/* Refund Type */}
          <div className="space-y-2">
            <Label>Refund Type</Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={isFullRefund ? "default" : "outline"}
                className="flex-1"
                onClick={() => setIsFullRefund(true)}
              >
                Full Refund
              </Button>
              <Button
                type="button"
                variant={!isFullRefund ? "default" : "outline"}
                className="flex-1"
                onClick={() => setIsFullRefund(false)}
              >
                Partial Refund
              </Button>
            </div>
          </div>

          {/* Refund Amount (for partial) */}
          {!isFullRefund && (
            <div className="space-y-2">
              <Label htmlFor="refund-amount">Refund Amount</Label>
              <Input
                id="refund-amount"
                type="number"
                step="0.01"
                min="0.01"
                max={transaction.total}
                placeholder="0.00"
                value={refundAmount}
                onChange={(e) => setRefundAmount(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Maximum: {formatCurrency(transaction.total)}
              </p>
            </div>
          )}

          {/* Reason */}
          <div className="space-y-2">
            <Label htmlFor="reason">Reason</Label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger id="reason">
                <SelectValue placeholder="Select a reason" />
              </SelectTrigger>
              <SelectContent>
                {REFUND_REASONS.map((r) => (
                  <SelectItem key={r} value={r}>
                    {r}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Add any additional details..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleRefund}
            disabled={refundTransaction.isPending}
          >
            {refundTransaction.isPending
              ? "Processing..."
              : `Refund ${
                  isFullRefund
                    ? formatCurrency(transaction.total)
                    : formatCurrency(parseFloat(refundAmount) || 0)
                }`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
