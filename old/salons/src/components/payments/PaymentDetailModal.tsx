"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { usePaymentDetail } from "@/lib/api/hooks/usePaymentDetail";
import { useGenerateReceipt } from "@/lib/api/hooks/useGenerateReceipt";
import { useEmailReceipt } from "@/lib/api/hooks/useEmailReceipt";
import { PaymentDetailResponse } from "@/lib/api/types";
import { format } from "date-fns";
import {
  Loader2,
  Download,
  Mail,
  ExternalLink,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface PaymentDetailModalProps {
  paymentId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onRefund?: (paymentId: string) => void;
}

/**
 * Payment Detail Modal Component
 * Displays comprehensive payment information with related booking and customer data
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
 */
export function PaymentDetailModal({
  paymentId,
  isOpen,
  onClose,
  onRefund,
}: PaymentDetailModalProps) {
  const { data, isLoading, error } = usePaymentDetail(paymentId);
  const [expandedMetadata, setExpandedMetadata] = useState(false);
  const [emailRecipient, setEmailRecipient] = useState("");
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [emailSuccess, setEmailSuccess] = useState(false);

  const { mutate: generateReceipt, isPending: isGenerating } =
    useGenerateReceipt();
  const { mutate: emailReceipt, isPending: isEmailing } = useEmailReceipt();

  if (!isOpen) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "refunded":
        return "bg-blue-100 text-blue-800";
      case "partially_refunded":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Payment Details</DialogTitle>
        </DialogHeader>

        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            Failed to load payment details: {error.message}
          </div>
        )}

        {data && (
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="booking">Booking</TabsTrigger>
              <TabsTrigger value="metadata">Metadata</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Reference
                  </label>
                  <p className="text-lg font-semibold">
                    {data.payment.reference}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Amount
                  </label>
                  <p className="text-lg font-semibold">
                    ₦{data.payment.amount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Status
                  </label>
                  <Badge className={getStatusColor(data.payment.status)}>
                    {data.payment.status}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Gateway
                  </label>
                  <p className="text-lg font-semibold capitalize">
                    {data.payment.gateway}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Payment Type
                  </label>
                  <p className="text-lg font-semibold capitalize">
                    {data.payment.payment_type}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Created
                  </label>
                  <p className="text-sm">
                    {format(new Date(data.payment.created_at), "PPp")}
                  </p>
                </div>
              </div>

              {/* Refund Information */}
              {data.payment.refund_amount && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">
                    Refund Information
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Amount:</span>
                      <p className="font-semibold">
                        ₦{data.payment.refund_amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-600">Type:</span>
                      <p className="font-semibold capitalize">
                        {data.payment.refund_type}
                      </p>
                    </div>
                    {data.payment.refund_reason && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Reason:</span>
                        <p className="font-semibold">
                          {data.payment.refund_reason}
                        </p>
                      </div>
                    )}
                    {data.payment.refunded_at && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Refunded At:</span>
                        <p className="font-semibold">
                          {format(new Date(data.payment.refunded_at), "PPp")}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Customer Information */}
              {data.customer && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Customer Information
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Name:</span>
                      <p className="font-semibold">{data.customer.name}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Email:</span>
                      <p className="font-semibold">{data.customer.email}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Phone:</span>
                      <p className="font-semibold">{data.customer.phone}</p>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* Booking Tab */}
            <TabsContent value="booking" className="space-y-4">
              {data.booking ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">
                        Booking Reference
                      </label>
                      <p className="text-lg font-semibold">
                        {data.booking.reference}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">
                        Status
                      </label>
                      <Badge className={getStatusColor(data.booking.status)}>
                        {data.booking.status}
                      </Badge>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">
                        Start Time
                      </label>
                      <p className="text-sm">
                        {format(new Date(data.booking.start_time), "PPp")}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">
                        End Time
                      </label>
                      <p className="text-sm">
                        {format(new Date(data.booking.end_time), "PPp")}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => {
                      // Navigate to booking details
                      window.location.href = `/dashboard/bookings/${data.booking?.id}`;
                    }}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Booking
                  </Button>
                </div>
              ) : (
                <p className="text-gray-500">
                  No booking information available
                </p>
              )}
            </TabsContent>

            {/* Metadata Tab */}
            <TabsContent value="metadata" className="space-y-4">
              {data.payment.metadata &&
              Object.keys(data.payment.metadata).length > 0 ? (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <button
                    onClick={() => setExpandedMetadata(!expandedMetadata)}
                    className="w-full text-left font-semibold text-gray-900 hover:text-gray-700"
                  >
                    {expandedMetadata ? "▼" : "▶"} Payment Metadata
                  </button>
                  {expandedMetadata && (
                    <pre className="mt-3 bg-white p-3 rounded border border-gray-200 text-xs overflow-auto max-h-64">
                      {JSON.stringify(data.payment.metadata, null, 2)}
                    </pre>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">No metadata available</p>
              )}

              {/* Receipt Information */}
              {data.receipt_info && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-900 mb-2">
                    Receipt Information
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Receipt Number:</span>
                      <p className="font-semibold">
                        {data.receipt_info.receipt_number}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-600">Generated:</span>
                      <p className="font-semibold">
                        {format(
                          new Date(data.receipt_info.generated_at),
                          "PPp",
                        )}
                      </p>
                    </div>
                    {data.receipt_info.emailed_at && (
                      <div>
                        <span className="text-gray-600">Emailed To:</span>
                        <p className="font-semibold">
                          {data.receipt_info.emailed_to}
                        </p>
                        <p className="text-xs text-gray-500">
                          {format(
                            new Date(data.receipt_info.emailed_at),
                            "PPp",
                          )}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}

        {/* Action Buttons */}
        {data && (
          <div className="space-y-4">
            {/* Email Receipt Form */}
            {showEmailForm && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                <h4 className="font-semibold text-blue-900">Email Receipt</h4>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Recipient Email
                  </label>
                  <input
                    type="email"
                    value={emailRecipient}
                    onChange={(e) => setEmailRecipient(e.target.value)}
                    placeholder={data.customer?.email || "Enter email address"}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
                {emailSuccess && (
                  <div className="bg-green-50 border border-green-200 rounded p-2 flex gap-2 text-sm text-green-700">
                    <CheckCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>Receipt emailed successfully!</span>
                  </div>
                )}
                <div className="flex gap-2">
                  <Button
                    onClick={() => {
                      const email = emailRecipient || data.customer?.email;
                      if (!email) {
                        alert("Please enter an email address");
                        return;
                      }
                      emailReceipt(
                        { paymentId: data.payment.id, email },
                        {
                          onSuccess: () => {
                            setEmailSuccess(true);
                            setTimeout(() => {
                              setShowEmailForm(false);
                              setEmailRecipient("");
                              setEmailSuccess(false);
                            }, 2000);
                          },
                          onError: (error: any) => {
                            alert(
                              error.response?.data?.message ||
                                "Failed to email receipt",
                            );
                          },
                        },
                      );
                    }}
                    disabled={isEmailing}
                    className="flex-1"
                  >
                    {isEmailing && (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    )}
                    Send
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowEmailForm(false);
                      setEmailRecipient("");
                      setEmailSuccess(false);
                    }}
                    disabled={isEmailing}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t">
              {data.payment.status === "completed" &&
                data.payment.refund_type !== "full" && (
                  <Button
                    onClick={() => onRefund?.(data.payment.id)}
                    variant="destructive"
                  >
                    Process Refund
                  </Button>
                )}
              <Button
                variant="outline"
                onClick={() => generateReceipt(data.payment.id)}
                disabled={isGenerating}
              >
                {isGenerating && (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                )}
                <Download className="h-4 w-4 mr-2" />
                Download Receipt
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowEmailForm(!showEmailForm)}
                disabled={isEmailing}
              >
                <Mail className="h-4 w-4 mr-2" />
                Email Receipt
              </Button>
              <Button variant="outline" onClick={onClose} className="ml-auto">
                Close
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
