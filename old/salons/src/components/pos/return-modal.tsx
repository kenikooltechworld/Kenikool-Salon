import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { useProcessReturn } from "@/lib/api/hooks/usePOS";
import type { POSTransaction } from "@/lib/api/hooks/usePOS";
import { formatCurrency } from "@/lib/utils/currency";

interface ReturnModalProps {
  open: boolean;
  onClose: () => void;
  transaction: POSTransaction | null;
}

export function ReturnModal({ open, onClose, transaction }: ReturnModalProps) {
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [returnReason, setReturnReason] = useState("");
  const [restockingFee, setRestockingFee] = useState("0");

  const processReturn = useProcessReturn();

  const handleItemToggle = (index: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedItems(newSelected);
  };

  const handleSubmit = async () => {
    if (!transaction) return;

    if (selectedItems.size === 0) {
      toast.error("Please select at least one item to return");
      return;
    }

    if (!returnReason.trim()) {
      toast.error("Please provide a return reason");
      return;
    }

    const returnItems = Array.from(selectedItems).map((index) => {
      const item = transaction.items[index];
      return {
        type: item.type,
        item_id: item.item_id,
        item_name: item.item_name,
        quantity: item.quantity,
        price: item.price,
      };
    });

    try {
      const result = await processReturn.mutateAsync({
        transaction_id: transaction.id,
        return_items: returnItems,
        return_reason: returnReason,
        restocking_fee: parseFloat(restockingFee) || 0,
      });

      toast.success(
        `Return processed. Net refund: ${formatCurrency(result.net_refund)}`
      );
      handleClose();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to process return");
    }
  };

  const handleClose = () => {
    setSelectedItems(new Set());
    setReturnReason("");
    setRestockingFee("0");
    onClose();
  };

  const calculateReturnAmount = () => {
    if (!transaction) return 0;
    return Array.from(selectedItems).reduce((sum, index) => {
      const item = transaction.items[index];
      return sum + item.price * item.quantity;
    }, 0);
  };

  const returnAmount = calculateReturnAmount();
  const fee = parseFloat(restockingFee) || 0;
  const netRefund = returnAmount - fee;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Process Return</DialogTitle>
        </DialogHeader>

        {transaction && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Transaction: {transaction.transaction_number}
            </div>

            {/* Items Selection */}
            <div className="space-y-2">
              <Label>Select Items to Return</Label>
              <div className="border rounded-lg p-3 space-y-2 max-h-[200px] overflow-y-auto">
                {transaction.items.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 hover:bg-muted rounded"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <Checkbox
                        checked={selectedItems.has(index)}
                        onCheckedChange={() => handleItemToggle(index)}
                      />
                      <div className="flex-1">
                        <p className="font-medium text-sm">{item.item_name}</p>
                        <p className="text-xs text-muted-foreground">
                          Qty: {item.quantity} × {formatCurrency(item.price)}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm font-medium">
                      {formatCurrency(item.price * item.quantity)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Return Reason */}
            <div className="space-y-2">
              <Label htmlFor="return-reason">Return Reason</Label>
              <Textarea
                id="return-reason"
                placeholder="e.g., Defective product, Wrong item, Customer changed mind..."
                value={returnReason}
                onChange={(e) => setReturnReason(e.target.value)}
                maxLength={500}
                className="min-h-[80px] resize-none"
              />
              <p className="text-xs text-muted-foreground text-right">
                {returnReason.length}/500
              </p>
            </div>

            {/* Restocking Fee */}
            <div className="space-y-2">
              <Label htmlFor="restocking-fee">Restocking Fee (Optional)</Label>
              <Input
                id="restocking-fee"
                type="number"
                min="0"
                step="0.01"
                value={restockingFee}
                onChange={(e) => setRestockingFee(e.target.value)}
                className="flex-1"
              />
            </div>

            {/* Summary */}
            {selectedItems.size > 0 && (
              <div className="border-t pt-3 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Return Amount:</span>
                  <span>{formatCurrency(returnAmount)}</span>
                </div>
                {fee > 0 && (
                  <div className="flex justify-between text-sm text-[var(--accent)]">
                    <span>Restocking Fee:</span>
                    <span>-{formatCurrency(fee)}</span>
                  </div>
                )}
                <div className="flex justify-between font-bold pt-2 border-t">
                  <span>Net Refund:</span>
                  <span>{formatCurrency(netRefund)}</span>
                </div>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={
              processReturn.isPending ||
              selectedItems.size === 0 ||
              !returnReason.trim()
            }
          >
            {processReturn.isPending ? "Processing..." : "Process Return"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
