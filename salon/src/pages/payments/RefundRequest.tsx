import { useParams, useNavigate } from "react-router-dom";
import { usePayment } from "@/hooks/usePayments";
import { useCreateRefund } from "@/hooks/useRefunds";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { AlertCircleIcon } from "@/components/icons";

export default function RefundRequest() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: payment, isLoading } = usePayment(paymentId || "");
  const createRefundMutation = useCreateRefund();
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");

  const canRefund = payment && payment.status === "completed";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!reason.trim()) {
      setError("Please provide a reason for the refund");
      return;
    }

    if (!paymentId) return;

    try {
      await createRefundMutation.mutateAsync({
        paymentId,
        amount: payment?.amount || 0,
        reason,
      });
      showToast({
        variant: "success",
        title: "Success",
        description: "Refund request submitted successfully",
      });
      navigate("/payments");
    } catch (err: any) {
      const errorMessage = err.message || "Failed to create refund request";
      setError(errorMessage);
      showToast({
        variant: "error",
        title: "Error",
        description: errorMessage,
      });
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading payment...</div>;
  }

  if (!payment) {
    return <div className="text-center py-8">Payment not found</div>;
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Request Refund</h1>
        <Button variant="outline" onClick={() => navigate("/payments")}>
          Back
        </Button>
      </div>

      {/* Payment Details */}
      <div className="bg-card border border-border rounded-lg p-6 space-y-4">
        <h2 className="text-lg font-semibold">Payment Details</h2>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Payment ID</p>
            <p className="font-medium">{payment.id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Amount</p>
            <p className="font-medium text-lg">
              {formatCurrency(payment.amount)}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <p className="font-medium">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {payment.status}
              </span>
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Method</p>
            <p className="font-medium">{payment.method}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="font-medium">{formatDate(payment.createdAt)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Invoice ID</p>
            <p className="font-medium">{payment.invoiceId}</p>
          </div>
        </div>
      </div>

      {!canRefund && (
        <div className="bg-destructive/10 border border-destructive rounded-lg p-6 flex gap-4">
          <AlertCircleIcon
            size={24}
            className="text-destructive flex-shrink-0"
          />
          <div>
            <h3 className="font-semibold text-destructive mb-1">
              Cannot Refund
            </h3>
            <p className="text-sm">
              Only completed payments can be refunded. This payment status is{" "}
              <span className="font-medium">{payment.status}</span>.
            </p>
          </div>
        </div>
      )}

      {canRefund && (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Refund Amount */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-semibold mb-4">Refund Amount</h3>
            <div className="bg-muted rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Full Refund</p>
              <p className="text-2xl font-bold">
                {formatCurrency(payment.amount)}
              </p>
            </div>
          </div>

          {/* Reason */}
          <div className="bg-card border border-border rounded-lg p-6">
            <label className="block text-sm font-medium mb-2">
              Reason for Refund *
            </label>
            <textarea
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                setError("");
              }}
              className="w-full px-3 py-2 border border-border rounded-lg"
              rows={5}
              placeholder="Please explain why you are requesting a refund..."
            />
            {error && <p className="text-destructive text-sm mt-2">{error}</p>}
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <span className="font-medium">Note:</span> Refund requests are
              processed within 3-5 business days. You will receive a
              confirmation email once the refund is initiated.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={createRefundMutation.isPending || !reason.trim()}
              className="flex-1"
            >
              {createRefundMutation.isPending
                ? "Processing..."
                : "Request Refund"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/payments")}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      )}

      {!canRefund && (
        <Button
          variant="outline"
          onClick={() => navigate("/payments")}
          className="w-full"
        >
          Back to Payments
        </Button>
      )}
    </div>
  );
}
