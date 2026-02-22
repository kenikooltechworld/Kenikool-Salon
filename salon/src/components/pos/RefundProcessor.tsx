import { useState } from "react";
import { useTransactions } from "@/hooks/useCheckout";
import { useCreateRefund } from "@/hooks/useRefund";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";

export default function RefundProcessor() {
  const [selectedTransactionId, setSelectedTransactionId] = useState("");
  const [refundAmount, setRefundAmount] = useState("");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState(false);

  const { data: transactionsData, isLoading } = useTransactions({
    paymentStatus: "completed",
    pageSize: 20,
  });
  const { mutate: createRefund, isPending } = useCreateRefund();

  const transactions = transactionsData?.transactions || [];
  const selectedTransaction = transactions.find(
    (t) => t.id === selectedTransactionId,
  );

  const handleSubmit = () => {
    if (!selectedTransactionId || !refundAmount || !reason) {
      setError("Please fill in all required fields");
      return;
    }

    const amount = parseFloat(refundAmount);
    if (
      amount <= 0 ||
      (selectedTransaction && amount > selectedTransaction.total)
    ) {
      setError("Invalid refund amount");
      return;
    }

    createRefund(
      {
        originalTransactionId: selectedTransactionId,
        refundAmount: amount,
        refundReason: reason,
        notes,
      },
      {
        onSuccess: () => {
          setSuccess(true);
          setSelectedTransactionId("");
          setRefundAmount("");
          setReason("");
          setNotes("");
          setError(undefined);
          setTimeout(() => setSuccess(false), 3000);
        },
        onError: () => {
          setError("Failed to create refund");
        },
      },
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
      {/* Transaction Selection */}
      <div className="md:col-span-2">
        <Card className="p-4 md:p-6">
          <h3 className="text-base md:text-lg font-semibold mb-4 text-foreground">
            Select Transaction
          </h3>

          {error && (
            <Alert variant="error" className="mb-4">
              {error}
            </Alert>
          )}
          {success && (
            <Alert variant="success" className="mb-4">
              <p>Refund created successfully!</p>
            </Alert>
          )}

          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : transactions.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No completed transactions found
            </p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  onClick={() => setSelectedTransactionId(transaction.id)}
                  className={`p-3 md:p-4 border rounded-lg cursor-pointer transition ${
                    selectedTransactionId === transaction.id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-muted-foreground"
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm md:text-base text-foreground truncate">
                        {transaction.customerId}
                      </p>
                      <p className="text-xs md:text-sm text-muted-foreground">
                        {new Date(transaction.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <p className="font-bold text-sm md:text-base text-foreground flex-shrink-0">
                      ₦
                      {transaction.total.toLocaleString("en-NG", {
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Refund Form */}
      {selectedTransaction && (
        <Card className="p-4 md:p-6 sticky top-6">
          <h3 className="text-base md:text-lg font-semibold mb-4 text-foreground">
            Refund Details
          </h3>

          <div className="space-y-4">
            <div>
              <Label className="text-xs md:text-sm text-muted-foreground">
                Original Amount
              </Label>
              <p className="text-xl md:text-2xl font-bold text-foreground">
                ₦
                {selectedTransaction.total.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </p>
            </div>

            <div>
              <Label htmlFor="refund-amount" className="text-sm">
                Refund Amount *
              </Label>
              <Input
                id="refund-amount"
                type="number"
                step="0.01"
                min="0"
                max={selectedTransaction.total}
                placeholder="0.00"
                value={refundAmount}
                onChange={(e) => setRefundAmount(e.target.value)}
                className="text-sm"
              />
            </div>

            <div>
              <Label htmlFor="reason" className="text-sm">
                Reason *
              </Label>
              <Input
                id="reason"
                placeholder="e.g., Customer request, Damaged item"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="text-sm"
              />
            </div>

            <div>
              <Label htmlFor="notes" className="text-sm">
                Notes
              </Label>
              <Textarea
                id="notes"
                placeholder="Additional notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="text-sm"
              />
            </div>

            <Button
              onClick={handleSubmit}
              disabled={isPending}
              className="w-full text-sm md:text-base"
            >
              {isPending ? (
                <>
                  <Spinner className="w-4 h-4 mr-2" />
                  Processing...
                </>
              ) : (
                "Create Refund"
              )}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
