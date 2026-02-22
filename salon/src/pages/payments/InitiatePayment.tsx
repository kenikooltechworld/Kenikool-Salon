import { useParams, useNavigate } from "react-router-dom";
import { useInvoice } from "@/hooks/useInvoices";
import { useInitializePayment } from "@/hooks/usePayments";
import { useCustomers } from "@/hooks/useCustomers";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";
import { useState } from "react";
import { cn } from "@/lib/utils/cn";
import { v4 as uuidv4 } from "uuid";

export default function InitiatePayment() {
  const { invoiceId } = useParams<{ invoiceId: string }>();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: invoice, isLoading: invoiceLoading } = useInvoice(
    invoiceId || "",
  );
  const { data: customers = [] } = useCustomers();
  const initializePayment = useInitializePayment();

  if (invoiceLoading) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-200">
            Invoice not found
          </p>
        </div>
      </div>
    );
  }

  if (invoice.status === "paid") {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              This invoice is already paid
            </p>
            <button
              onClick={() => navigate("/invoices")}
              className="text-sm text-green-600 dark:text-green-400 hover:underline mt-2"
            >
              Back to invoices
            </button>
          </div>
        </div>
      </div>
    );
  }

  const customer = customers.find((c) => c.id === invoice.customerId);

  const handlePay = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email) {
      setError("Please enter your email address");
      return;
    }

    try {
      const idempotencyKey = uuidv4();
      await initializePayment.mutateAsync({
        amount: invoice.total,
        customerId: invoice.customerId,
        invoiceId: invoice.id,
        email,
        idempotencyKey,
        metadata: {
          invoiceId: invoice.id,
          customerId: invoice.customerId,
        },
      });
      // The hook will redirect to Paystack automatically
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to initialize payment");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        Initiate Payment
      </h1>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        {/* Invoice Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Invoice Summary
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">
                Invoice Number
              </span>
              <span className="font-medium text-gray-900 dark:text-white">
                #{invoice.id}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">
                Created Date
              </span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formatDate(new Date(invoice.createdAt))}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Due Date</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formatDate(new Date(invoice.dueDate))}
              </span>
            </div>
            <div className="border-t border-gray-200 dark:border-gray-700 pt-3 flex justify-between">
              <span className="font-semibold text-gray-900 dark:text-white">
                Amount Due
              </span>
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {formatCurrency(invoice.total)}
              </span>
            </div>
          </div>
        </div>

        {/* Customer Information */}
        {customer && (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Customer Information
            </h2>
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-gray-600 dark:text-gray-400">Name:</span>{" "}
                <span className="font-medium text-gray-900 dark:text-white">
                  {customer.firstName} {customer.lastName}
                </span>
              </p>
              <p>
                <span className="text-gray-600 dark:text-gray-400">Email:</span>{" "}
                <span className="font-medium text-gray-900 dark:text-white">
                  {customer.email}
                </span>
              </p>
              <p>
                <span className="text-gray-600 dark:text-gray-400">Phone:</span>{" "}
                <span className="font-medium text-gray-900 dark:text-white">
                  {customer.phone}
                </span>
              </p>
            </div>
          </div>
        )}

        {/* Payment Form */}
        <form onSubmit={handlePay} className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Payment Details
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  We'll send your payment receipt to this email
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  You will be redirected to Paystack to complete the payment
                  securely.
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => navigate(`/invoices/${invoiceId}`)}
              className="flex-1 px-6 py-3 rounded-lg font-semibold bg-gray-600 text-white hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={initializePayment.isPending}
              className={cn(
                "flex-1 px-6 py-3 rounded-lg font-semibold transition-colors",
                initializePayment.isPending
                  ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                  : "bg-green-600 text-white hover:bg-green-700",
              )}
            >
              {initializePayment.isPending ? "Processing..." : "Pay Now"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
