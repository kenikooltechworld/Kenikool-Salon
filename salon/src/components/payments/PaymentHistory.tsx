import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  RefreshCwIcon,
  DownloadIcon,
} from "@/components/icons";
import { usePayments, useRetryPayment } from "@/hooks/usePayments";
import { formatCurrency, formatDate } from "@/lib/utils";

interface PaymentHistoryProps {
  customerId?: string;
  invoiceId?: string;
  limit?: number;
}

export function PaymentHistory({
  customerId,
  invoiceId,
  limit = 10,
}: PaymentHistoryProps) {
  const [retryingPaymentId, setRetryingPaymentId] = useState<string | null>(
    null,
  );
  const { showToast } = useToast();

  const {
    data: payments,
    isLoading,
    error,
  } = usePayments({
    customerId,
    status: invoiceId ? undefined : undefined,
  });

  const retryPaymentMutation = useRetryPayment();

  const handleRetryPayment = async (paymentId: string) => {
    setRetryingPaymentId(paymentId);
    try {
      await retryPaymentMutation.mutateAsync(paymentId);
      showToast({
        variant: "success",
        title: "Success",
        description: "Payment retry initiated successfully",
      });
    } catch (error) {
      showToast({
        variant: "error",
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to retry payment",
      });
    } finally {
      setRetryingPaymentId(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon size={20} className="text-green-600" />;
      case "failed":
        return <XCircleIcon size={20} className="text-red-600" />;
      case "pending":
        return <ClockIcon size={20} className="text-yellow-600" />;
      case "refunded":
        return <RefreshCwIcon size={20} className="text-blue-600" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="secondary">{status}</Badge>;
      case "failed":
        return <Badge variant="destructive">{status}</Badge>;
      case "pending":
        return <Badge variant="outline">{status}</Badge>;
      case "refunded":
        return <Badge variant="accent">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Spinner size="md" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="error">
        Failed to load payment history. Please try again later.
      </Alert>
    );
  }

  if (!payments || payments.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No payments found</p>
      </div>
    );
  }

  const displayPayments = payments.slice(0, limit);

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg overflow-x-auto">
        <table className="w-full min-w-max">
          <thead className="bg-muted border-b border-border">
            <tr>
              <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Date
              </th>
              <th className="hidden sm:table-cell px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Amount
              </th>
              <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Status
              </th>
              <th className="hidden md:table-cell px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Method
              </th>
              <th className="hidden lg:table-cell px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Reference
              </th>
              <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {displayPayments.map((payment) => (
              <tr key={payment.id} className="hover:bg-muted/50 transition">
                <td className="px-4 md:px-6 py-4 text-sm text-foreground">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(payment.status)}
                    <span>{formatDate(new Date(payment.createdAt))}</span>
                  </div>
                </td>
                <td className="hidden sm:table-cell px-4 md:px-6 py-4 text-sm font-medium text-foreground">
                  {formatCurrency(payment.amount, "NGN")}
                </td>
                <td className="px-4 md:px-6 py-4 text-sm">
                  {getStatusBadge(payment.status)}
                </td>
                <td className="hidden md:table-cell px-4 md:px-6 py-4 text-sm text-muted-foreground">
                  {payment.method || "paystack"}
                </td>
                <td className="hidden lg:table-cell px-4 md:px-6 py-4 text-sm text-muted-foreground font-mono text-xs">
                  {payment.transactionId || "-"}
                </td>
                <td className="px-4 md:px-6 py-4 text-sm">
                  <div className="flex items-center gap-2">
                    {payment.status === "failed" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRetryPayment(payment.id)}
                        disabled={retryingPaymentId === payment.id}
                        className="gap-1"
                      >
                        {retryingPaymentId === payment.id ? (
                          <>
                            <Spinner size="sm" />
                            Retrying...
                          </>
                        ) : (
                          <>
                            <RefreshCwIcon size={14} />
                            Retry
                          </>
                        )}
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      className="gap-1"
                      title="Download receipt"
                    >
                      <DownloadIcon size={14} />
                      <span className="hidden sm:inline">Receipt</span>
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {payments.length > limit && (
        <div className="text-center">
          <Button variant="outline">View All Payments</Button>
        </div>
      )}
    </div>
  );
}
