import { useParams, useNavigate } from "react-router-dom";
import { usePayment, useRetryPayment } from "@/hooks/usePayments";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { AlertCircleIcon } from "@/components/icons";

export default function PaymentRetry() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const navigate = useNavigate();
  const { data: payment, isLoading } = usePayment(paymentId || "");
  const retryMutation = useRetryPayment();

  const handleRetry = async () => {
    if (!paymentId) return;
    try {
      await retryMutation.mutateAsync(paymentId);
      // Redirect to Paystack happens automatically in the hook
    } catch (error) {
      console.error("Retry failed:", error);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading payment...</div>;
  }

  if (!payment) {
    return <div className="text-center py-8">Payment not found</div>;
  }

  const retryCount =
    (payment as any).retryCount || (payment as any).retry_count || 0;
  const maxRetries = 3;
  const canRetry = retryCount < maxRetries && payment.status === "failed";

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Retry Payment</h1>
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
            <p className="font-medium">{formatCurrency(payment.amount)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <p className="font-medium">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
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

      {/* Retry Status */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-start gap-4">
          <AlertCircleIcon
            size={24}
            className="text-yellow-600 flex-shrink-0 mt-1"
          />
          <div className="flex-1">
            <h3 className="font-semibold mb-2">Retry Attempts</h3>
            <p className="text-sm text-muted-foreground mb-4">
              You have attempted to retry this payment {retryCount} of{" "}
              {maxRetries} times.
            </p>

            {/* Progress Bar */}
            <div className="w-full bg-muted rounded-full h-2 mb-4">
              <div
                className="bg-yellow-600 h-2 rounded-full transition-all"
                style={{ width: `${(retryCount / maxRetries) * 100}%` }}
              />
            </div>

            {canRetry ? (
              <p className="text-sm text-green-600">
                You can retry this payment {maxRetries - retryCount} more
                time(s).
              </p>
            ) : (
              <p className="text-sm text-destructive">
                Maximum retry attempts reached. Please contact support for
                assistance.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      {canRetry ? (
        <div className="space-y-4">
          <Button
            onClick={handleRetry}
            disabled={retryMutation.isPending}
            className="w-full"
          >
            {retryMutation.isPending ? "Processing..." : "Retry Payment"}
          </Button>
          <p className="text-sm text-muted-foreground text-center">
            You will be redirected to Paystack to complete the payment.
          </p>
        </div>
      ) : (
        <div className="bg-destructive/10 border border-destructive rounded-lg p-6 space-y-4">
          <h3 className="font-semibold text-destructive">Unable to Retry</h3>
          <p className="text-sm">
            You have reached the maximum number of retry attempts for this
            payment. Please contact our support team for assistance.
          </p>
          <div className="space-y-2">
            <p className="text-sm font-medium">Support Contact:</p>
            <p className="text-sm text-muted-foreground">
              Email: support@kenikool.com
            </p>
            <p className="text-sm text-muted-foreground">
              Phone: +234 (0) XXX XXX XXXX
            </p>
          </div>
        </div>
      )}

      <Button
        variant="outline"
        onClick={() => navigate("/payments")}
        className="w-full"
      >
        Back to Payments
      </Button>
    </div>
  );
}
