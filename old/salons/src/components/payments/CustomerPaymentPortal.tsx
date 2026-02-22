"use client";

import React, { useState } from "react";
import {
  useCustomerPayments,
  useGeneratePaymentLink,
} from "@/lib/api/hooks/useCustomerPaymentPortal";
import { useGenerateReceipt } from "@/lib/api/hooks/useGenerateReceipt";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Download, Link as LinkIcon, Copy } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import type { CustomerPayment } from "@/lib/api/hooks/useCustomerPaymentPortal";

interface CustomerPaymentPortalProps {
  customerId: string;
}

export function CustomerPaymentPortal({
  customerId,
}: CustomerPaymentPortalProps) {
  const { data: payments, isLoading, error } = useCustomerPayments(customerId);
  const generateLinkMutation = useGeneratePaymentLink();
  const generateReceiptMutation = useGenerateReceipt();
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [selectedPayment, setSelectedPayment] = useState<CustomerPayment | null>(
    null
  );

  const handleGenerateLink = (paymentId: string) => {
    generateLinkMutation.mutate(
      { payment_id: paymentId },
      {
        onSuccess: () => {
          // Link generated successfully
        },
      }
    );
  };

  const handleDownloadReceipt = (paymentId: string) => {
    generateReceiptMutation.mutate({ payment_id: paymentId });
  };

  const handleCopyLink = (token: string) => {
    const url = `${window.location.origin}/payments/link/${token}`;
    navigator.clipboard.writeText(url);
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  };

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
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load your payment history. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Payment History</h1>
        <p className="text-gray-600 mt-2">
          View and manage your payments with us
        </p>
      </div>

      {/* Payments List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : payments && payments.length > 0 ? (
        <div className="space-y-3">
          {payments.map((payment) => (
            <Card key={payment.id}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">
                        {payment.service_name || "Service"}
                      </h3>
                      <Badge className={getStatusColor(payment.status)}>
                        {payment.status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>
                        <p className="text-xs text-gray-500">Amount</p>
                        <p className="font-medium text-gray-900">
                          ${payment.amount.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Date</p>
                        <p className="font-medium text-gray-900">
                          {new Date(payment.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Reference</p>
                        <p className="font-medium text-gray-900">
                          {payment.reference}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Gateway</p>
                        <p className="font-medium text-gray-900">
                          {payment.gateway}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    {payment.status === "pending" && (
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            size="sm"
                            onClick={() => setSelectedPayment(payment)}
                          >
                            <LinkIcon className="h-4 w-4 mr-2" />
                            Pay Now
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Complete Payment</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <label className="text-sm font-medium">
                                Amount Due
                              </label>
                              <p className="text-2xl font-bold">
                                ${selectedPayment?.amount.toFixed(2)}
                              </p>
                            </div>
                            <Button
                              onClick={() =>
                                handleGenerateLink(selectedPayment?.id || "")
                              }
                              disabled={generateLinkMutation.isPending}
                              className="w-full"
                            >
                              {generateLinkMutation.isPending
                                ? "Generating..."
                                : "Generate Payment Link"}
                            </Button>
                            {generateLinkMutation.data && (
                              <div className="p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm text-gray-600 mb-2">
                                  Payment Link:
                                </p>
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={`${window.location.origin}/payments/link/${generateLinkMutation.data.token}`}
                                    readOnly
                                    className="flex-1 px-2 py-1 text-sm border rounded"
                                  />
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() =>
                                      handleCopyLink(
                                        generateLinkMutation.data.token
                                      )
                                    }
                                  >
                                    <Copy className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>
                    )}

                    {payment.receipt_url && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownloadReceipt(payment.id)}
                        disabled={generateReceiptMutation.isPending}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Receipt
                      </Button>
                    )}
                  </div>
                </div>

                {payment.refund_amount && (
                  <div className="mt-3 p-2 bg-blue-50 rounded text-sm">
                    <p className="text-blue-900">
                      Refunded: ${payment.refund_amount.toFixed(2)}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-gray-600">
              No payments found. Your payment history will appear here.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Error Messages */}
      {generateLinkMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to generate payment link. Please try again.
          </AlertDescription>
        </Alert>
      )}

      {generateReceiptMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to download receipt. Please try again.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
