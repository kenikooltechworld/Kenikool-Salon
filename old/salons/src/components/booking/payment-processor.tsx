/**
 * PaymentProcessor Component
 * Processes payment and updates booking status
 * Validates: Requirements 3.4, 3.5, 3.6
 * Property 6: Payment Status Persistence
 */
import React, { useState } from "react";
import { AlertCircle, CheckCircle, Loader } from "lucide-react";

interface PaymentProcessorProps {
  bookingId: string;
  amount: number;
  paymentMethod: string;
  onSuccess?: (paymentId: string) => void;
  onError?: (error: string) => void;
  onProcessingChange?: (processing: boolean) => void;
}

/**
 * Component for processing payment and updating booking status
 * Validates: Requirements 3.4, 3.5, 3.6
 * Property 6: Payment Status Persistence - Booking status should be updated to confirmed
 */
export const PaymentProcessor: React.FC<PaymentProcessorProps> = ({
  bookingId,
  amount,
  paymentMethod,
  onSuccess,
  onError,
  onProcessingChange,
}) => {
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState<
    "idle" | "processing" | "success" | "error"
  >("idle");
  const [error, setError] = useState<string | null>(null);
  const [paymentId, setPaymentId] = useState<string | null>(null);

  const handleProcess = async () => {
    setProcessing(true);
    onProcessingChange?.(true);
    setStatus("processing");
    setError(null);

    try {
      // Call payment API
      const response = await fetch("/api/payments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          booking_id: bookingId,
          amount,
          payment_method: paymentMethod,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Payment processing failed");
      }

      const data = await response.json();
      const newPaymentId = data.id || `PAY-${Date.now()}`;

      setPaymentId(newPaymentId);
      setStatus("success");
      onSuccess?.(newPaymentId);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Payment processing failed";
      setError(message);
      setStatus("error");
      onError?.(message);
    } finally {
      setProcessing(false);
      onProcessingChange?.(false);
    }
  };

  if (status === "success") {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4">
        <div className="flex items-start gap-3">
          <CheckCircle className="h-5 w-5 flex-shrink-0 text-green-600" />
          <div>
            <h3 className="font-semibold text-green-900">Payment Successful</h3>
            <p className="mt-1 text-sm text-green-800">
              Your booking has been confirmed. Payment ID: {paymentId}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="space-y-3 rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Payment Failed</h3>
            <p className="mt-1 text-sm text-red-800">{error}</p>
          </div>
        </div>
        <button
          onClick={handleProcess}
          disabled={processing}
          className="w-full rounded bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:opacity-50"
        >
          {processing ? "Retrying..." : "Retry Payment"}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div>
        <h3 className="font-semibold text-gray-900">Payment Details</h3>
        <div className="mt-2 space-y-1 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Amount</span>
            <span className="font-medium">${amount.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span>Method</span>
            <span className="font-medium">{paymentMethod}</span>
          </div>
          <div className="flex justify-between">
            <span>Booking ID</span>
            <span className="font-medium text-xs">{bookingId}</span>
          </div>
        </div>
      </div>

      <button
        onClick={handleProcess}
        disabled={processing}
        className="w-full rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {processing ? (
          <span className="flex items-center justify-center gap-2">
            <Loader className="h-4 w-4 animate-spin" />
            Processing...
          </span>
        ) : (
          `Process Payment - $${amount.toFixed(2)}`
        )}
      </button>
    </div>
  );
};

export default PaymentProcessor;
