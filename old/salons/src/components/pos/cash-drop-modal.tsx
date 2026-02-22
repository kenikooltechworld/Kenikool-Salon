import { useState } from "react";
import { useRecordCashDrop } from "@/lib/api/hooks/usePOS";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { DollarSignIcon } from "@/components/icons";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface CashDropModalProps {
  open: boolean;
  onClose: () => void;
}

export function CashDropModal({ open, onClose }: CashDropModalProps) {
  const [amount, setAmount] = useState("");
  const [notes, setNotes] = useState("");
  const recordCashDrop = useRecordCashDrop();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const dropAmount = parseFloat(amount);
    if (isNaN(dropAmount) || dropAmount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      await recordCashDrop.mutateAsync({
        amount: dropAmount,
        notes: notes || undefined,
      });
      toast.success(`Cash drop of ${formatCurrency(dropAmount)} recorded`);
      setAmount("");
      setNotes("");
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to record cash drop");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSignIcon className="h-5 w-5" />
            Record Cash Drop
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="amount">Amount *</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
            <p className="text-sm text-muted-foreground mt-1">
              Amount to remove from cash drawer
            </p>
          </div>

          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              placeholder="Bank deposit, safe drop, etc..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={recordCashDrop.isPending}>
              {recordCashDrop.isPending ? "Recording..." : "Record Drop"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
