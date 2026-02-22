import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useVoidTransaction, POSTransaction } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { AlertCircleIcon, XCircleIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface VoidModalProps {
  transaction: POSTransaction | null;
  open: boolean;
  onClose: () => void;
}

const VOID_REASONS = [
  "Customer Cancelled",
  "Incorrect Items",
  "Pricing Error",
  "Duplicate Transaction",
  "System Error",
  "Other",
];

export function VoidModal({ transaction, open, onClose }: VoidModalProps) {
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");

  const voidTransaction = useVoidTransaction();

  const handleClose = () => {
    setReason("");
    setNotes("");
    onClose();
  };

  const handleVoid = async () => {
    if (!transaction) return;

    // Validate inputs
    if (!reason) {
      toast.error("Please select a void reason");
      return;
    }

    try {
      await voidTransaction.mutateAsync({
        transaction_id: transaction.id,
        reason: notes ? `${reason}: ${notes}` : reason,
      });

      toast.success("Transaction voided successfully");
      handleClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to void transaction");
    }
  };

  if (!transaction) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <XCircleIcon className="h-5 w-5 text-destructive" />
            Void Transaction
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Warning */}
          <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <AlertCircleIcon className="h-5 w-5 text-destructive mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-destructive">Warning</p>
              <p className="text-muted-foreground">
                This action cannot be undone. The transaction will be marked as
                voided and cannot be completed.
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
            <p className="text-xs text-muted-foreground">
              Status: {transaction.status.toUpperCase()}
            </p>
          </div>

          {/* Reason */}
          <div className="space-y-2">
            <Label htmlFor="void-reason">Reason</Label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger id="void-reason">
                <SelectValue placeholder="Select a reason" />
              </SelectTrigger>
              <SelectContent>
                {VOID_REASONS.map((r) => (
                  <SelectItem key={r} value={r}>
                    {r}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="void-notes">Additional Notes (Optional)</Label>
            <Textarea
              id="void-notes"
              placeholder="Add any additional details..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>

          {/* Info */}
          <div className="p-3 bg-[var(--muted)] dark:bg-[var(--muted)]/20 border border-[var(--border)] rounded-lg text-sm">
            <p className="text-[var(--foreground)]">
              <strong>Note:</strong> Only pending transactions can be voided.
              For completed transactions, use the refund option instead.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleVoid}
            disabled={voidTransaction.isPending}
          >
            {voidTransaction.isPending ? "Voiding..." : "Void Transaction"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
