import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  useGetParkedTransactions,
  useResumeParkedTransaction,
  useDeleteParkedTransaction,
} from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { XIcon, PlayIcon, TrashIcon, UserIcon, PhoneIcon } from "@/components/icons";
import { format } from "date-fns";
import { formatCurrency } from "@/lib/utils/currency";

interface ParkedTransactionsModalProps {
  open: boolean;
  onClose: () => void;
  onResume?: (transactionId: string) => void;
}

export function ParkedTransactionsModal({
  open,
  onClose,
  onResume,
}: ParkedTransactionsModalProps) {
  const { data: parkedTransactions = [], isLoading } =
    useGetParkedTransactions();
  const resumeTransaction = useResumeParkedTransaction();
  const deleteTransaction = useDeleteParkedTransaction();

  const handleResume = async (parkedId: string) => {
    try {
      const transaction = await resumeTransaction.mutateAsync(parkedId);
      toast.success("Transaction resumed successfully");
      onClose();
      if (onResume) {
        onResume(transaction.id);
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to resume transaction");
    }
  };

  const handleDelete = async (parkedId: string) => {
    if (!confirm("Are you sure you want to delete this parked transaction?")) {
      return;
    }

    try {
      await deleteTransaction.mutateAsync(parkedId);
      toast.success("Parked transaction deleted");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to delete transaction");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Parked Transactions</span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XIcon className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : parkedTransactions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No parked transactions</p>
          </div>
        ) : (
          <div className="space-y-3">
            {parkedTransactions.map((parked) => (
              <div
                key={parked.id}
                className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="secondary">{parked.hold_number}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {format(new Date(parked.parked_at), "MMM dd, HH:mm")}
                      </span>
                    </div>

                    {parked.customer_name && (
                      <div className="flex items-center gap-2 text-sm mb-1">
                        <UserIcon className="h-4 w-4 text-muted-foreground" />
                        <span>{parked.customer_name}</span>
                      </div>
                    )}

                    {parked.customer_phone && (
                      <div className="flex items-center gap-2 text-sm mb-1">
                        <PhoneIcon className="h-4 w-4 text-muted-foreground" />
                        <span>{parked.customer_phone}</span>
                      </div>
                    )}

                    {parked.notes && (
                      <p className="text-sm text-muted-foreground mt-2">
                        {parked.notes}
                      </p>
                    )}

                    <div className="flex items-center gap-4 mt-3 text-sm">
                      <span className="text-muted-foreground">
                        {parked.items_count} item
                        {parked.items_count !== 1 ? "s" : ""}
                      </span>
                      <span className="font-medium">
                        {formatCurrency(parked.total)}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      size="sm"
                      onClick={() => handleResume(parked.id)}
                      disabled={resumeTransaction.isPending}
                    >
                      <PlayIcon className="h-4 w-4 mr-1" />
                      Resume
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(parked.id)}
                      disabled={deleteTransaction.isPending}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
