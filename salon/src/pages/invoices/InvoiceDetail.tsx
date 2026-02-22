import { useParams, useNavigate } from "react-router-dom";
import { useInvoice, useUpdateInvoice } from "@/hooks/useInvoices";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import {
  AlertCircleIcon,
  CheckCircleIcon,
  Edit2Icon,
  TrashIcon,
} from "@/components/icons";
import { useState } from "react";

export default function InvoiceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: invoice, isLoading, error } = useInvoice(id || "");
  const updateInvoice = useUpdateInvoice();

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-4 sm:p-6">
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="max-w-4xl mx-auto p-4 sm:p-6">
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon
            size={20}
            className="text-red-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-sm text-red-800 dark:text-red-200">
            Invoice not found
          </p>
        </div>
      </div>
    );
  }

  const handleCancel = async () => {
    if (window.confirm("Are you sure you want to cancel this invoice?")) {
      try {
        await updateInvoice.mutateAsync({
          id: invoice.id,
          status: "cancelled",
        });
        navigate("/invoices");
      } catch (error) {
        alert("Failed to cancel invoice");
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "draft":
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
      case "issued":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200";
      case "paid":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200";
      case "cancelled":
        return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Invoice #{invoice.id}
          </h1>
          <p className="text-muted-foreground mt-1">
            Created {formatDate(new Date(invoice.created_at))}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              invoice.status,
            )}`}
          >
            {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Invoice Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer Info */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Customer Information
            </h2>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                <span className="font-medium text-foreground">
                  Customer ID:
                </span>{" "}
                {invoice.customer_id}
              </p>
              <p>
                <span className="font-medium text-foreground">Due Date:</span>{" "}
                {formatDate(new Date(invoice.due_date))}
              </p>
              {invoice.appointment_id && (
                <p>
                  <span className="font-medium text-foreground">
                    Appointment ID:
                  </span>{" "}
                  {invoice.appointment_id}
                </p>
              )}
            </div>
          </div>

          {/* Line Items */}
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="p-6 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">
                Line Items
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-muted">
                    <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Description
                    </th>
                    <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                      Quantity
                    </th>
                    <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                      Rate
                    </th>
                    <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.line_items && invoice.line_items.length > 0 ? (
                    invoice.line_items.map((item, index) => (
                      <tr key={index} className="border-b border-border">
                        <td className="px-4 md:px-6 py-4 text-sm text-foreground">
                          {item.service_name}
                        </td>
                        <td className="px-4 md:px-6 py-4 text-right text-sm text-muted-foreground">
                          {item.quantity}
                        </td>
                        <td className="px-4 md:px-6 py-4 text-right text-sm text-muted-foreground">
                          {formatCurrency(item.unit_price)}
                        </td>
                        <td className="px-4 md:px-6 py-4 text-right text-sm font-medium text-foreground">
                          {formatCurrency(item.total)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-4 md:px-6 py-4 text-center text-muted-foreground"
                      >
                        No line items
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Totals */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span className="text-foreground font-medium">
                  {formatCurrency(invoice.subtotal)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax</span>
                <span className="text-foreground font-medium">
                  {formatCurrency(invoice.tax)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Discount</span>
                <span className="text-foreground font-medium">
                  -{formatCurrency(invoice.discount)}
                </span>
              </div>
              <div className="border-t border-border pt-3 flex justify-between">
                <span className="font-semibold text-foreground">Total</span>
                <span className="text-lg font-bold text-foreground">
                  {formatCurrency(invoice.total)}
                </span>
              </div>
            </div>
          </div>

          {/* Notes */}
          {invoice.notes && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Notes
              </h2>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {invoice.notes}
              </p>
            </div>
          )}
        </div>

        {/* Sidebar Actions */}
        <div className="space-y-4">
          {/* Status Card */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-semibold text-foreground mb-4">Status</h3>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                {invoice.status === "paid" ? (
                  <span className="flex items-center gap-2 text-green-600 dark:text-green-400">
                    <CheckCircleIcon size={16} />
                    Paid
                  </span>
                ) : invoice.status === "cancelled" ? (
                  <span className="flex items-center gap-2 text-red-600 dark:text-red-400">
                    <AlertCircleIcon size={16} />
                    Cancelled
                  </span>
                ) : (
                  <span className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                    <AlertCircleIcon size={16} />
                    Unpaid
                  </span>
                )}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            {invoice.status === "draft" && (
              <Button
                onClick={() => navigate(`/invoices/${id}/edit`)}
                variant="outline"
                className="w-full gap-2"
              >
                <Edit2Icon size={16} />
                Edit
              </Button>
            )}

            {invoice.status !== "paid" && invoice.status !== "cancelled" && (
              <Button
                onClick={() => {
                  // TODO: Implement payment flow
                  alert("Payment flow to be implemented");
                }}
                className="w-full"
              >
                Pay Now
              </Button>
            )}

            {invoice.status === "draft" && (
              <Button
                onClick={handleCancel}
                variant="destructive"
                className="w-full gap-2"
              >
                <TrashIcon size={16} />
                Cancel Invoice
              </Button>
            )}

            <Button
              onClick={() => navigate("/invoices")}
              variant="outline"
              className="w-full"
            >
              Back to Invoices
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
