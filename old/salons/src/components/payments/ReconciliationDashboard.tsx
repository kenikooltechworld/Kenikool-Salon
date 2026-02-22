"use client";

import React, { useState } from "react";
import {
  useReconciliationData,
  useManualMatchPayment,
  useSyncWithGateway,
} from "@/lib/api/hooks/useReconciliation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RefreshCw, Link as LinkIcon } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { UnmatchedPayment } from "@/lib/api/hooks/useReconciliation";

export function ReconciliationDashboard() {
  const { data: reconciliation, isLoading, error, refetch } = useReconciliationData();
  const matchMutation = useManualMatchPayment();
  const syncMutation = useSyncWithGateway();
  const [selectedPayment, setSelectedPayment] = useState<UnmatchedPayment | null>(null);
  const [selectedBookingId, setSelectedBookingId] = useState<string>("");

  const handleManualMatch = () => {
    if (!selectedPayment || !selectedBookingId) return;

    matchMutation.mutate(
      {
        payment_id: selectedPayment.id,
        booking_id: selectedBookingId,
      },
      {
        onSuccess: () => {
          setSelectedPayment(null);
          setSelectedBookingId("");
        },
      }
    );
  };

  const handleSync = (paymentId: string) => {
    syncMutation.mutate({ payment_id: paymentId });
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load reconciliation data. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Payment Reconciliation</h1>
        <Button
          onClick={() => refetch()}
          disabled={isLoading}
          variant="outline"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : reconciliation ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Unmatched Payments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {reconciliation.total_unmatched}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Amount Mismatches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {reconciliation.total_mismatched}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Duplicate Payments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {reconciliation.total_duplicates}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Unmatched Payments Section */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : reconciliation && reconciliation.unmatched_payments.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Unmatched Payments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {reconciliation.unmatched_payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{payment.reference}</p>
                    <p className="text-sm text-gray-600">
                      ${payment.amount.toFixed(2)} • {payment.gateway}
                    </p>
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedPayment(payment)}
                      >
                        <LinkIcon className="h-4 w-4 mr-2" />
                        Match
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Match Payment to Booking</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium">
                            Payment Reference
                          </label>
                          <p className="text-sm text-gray-600">
                            {selectedPayment?.reference}
                          </p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">
                            Amount
                          </label>
                          <p className="text-sm text-gray-600">
                            ${selectedPayment?.amount.toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <label className="text-sm font-medium mb-2 block">
                            Select Booking
                          </label>
                          <Select
                            value={selectedBookingId}
                            onValueChange={setSelectedBookingId}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Choose a booking..." />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="booking-1">
                                Booking #1 - $100
                              </SelectItem>
                              <SelectItem value="booking-2">
                                Booking #2 - $150
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button
                          onClick={handleManualMatch}
                          disabled={!selectedBookingId || matchMutation.isPending}
                          className="w-full"
                        >
                          {matchMutation.isPending ? "Matching..." : "Match Payment"}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Mismatched Amounts Section */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : reconciliation && reconciliation.mismatched_amounts.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Amount Mismatches</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {reconciliation.mismatched_amounts.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between p-3 border border-yellow-200 bg-yellow-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{payment.reference}</p>
                    <p className="text-sm text-gray-600">
                      Local: ${payment.amount.toFixed(2)} • Gateway: $
                      {payment.gateway_amount?.toFixed(2)}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleSync(payment.id)}
                    disabled={syncMutation.isPending}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Sync
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Duplicate Payments Section */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : reconciliation && reconciliation.duplicate_payments.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Duplicate Payments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {reconciliation.duplicate_payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between p-3 border border-red-200 bg-red-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{payment.reference}</p>
                    <p className="text-sm text-gray-600">
                      ${payment.amount.toFixed(2)} • {payment.gateway}
                    </p>
                  </div>
                  <Button size="sm" variant="outline" disabled>
                    Review
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Success Messages */}
      {matchMutation.isSuccess && (
        <Alert>
          <AlertDescription className="text-green-700">
            Payment successfully matched to booking.
          </AlertDescription>
        </Alert>
      )}

      {syncMutation.isSuccess && (
        <Alert>
          <AlertDescription className="text-green-700">
            Payment successfully synced with gateway.
          </AlertDescription>
        </Alert>
      )}

      {/* Error Messages */}
      {matchMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to match payment. Please try again.
          </AlertDescription>
        </Alert>
      )}

      {syncMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to sync payment. Please try again.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
