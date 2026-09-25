import { useState, useEffect, type FormEvent } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Loader2Icon,
  AlertCircleIcon,
  CheckCircleIcon,
  LockIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/utils/api";
import { generateSalonReference } from "@/lib/utils/reference";

interface BookingPaymentState {
  bookingData: {
    customerId?: string;
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    serviceId: string;
    staffId: string;
    startTime: string;
    endTime: string;
    paymentOption: string;
  };
  amount: number;
  description: string;
}

const PAYMENT_POLL_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

type PaymentPageState =
  | { status: "form" }
  | { status: "processing" }
  | { status: "cancelled"; reason?: string }
  | { status: "failed"; reason?: string }
  | { status: "success" }
  | { status: "refunded"; reason?: string }
  | { status: "timeout" };

export function BookingPayment() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const state = location.state as BookingPaymentState;

  const [formData, setFormData] = useState({
    email: state?.bookingData?.customerEmail || "",
    amount: state?.amount || 0,
  });
  const [error, setError] = useState<string | null>(null);
  const [pageState, setPageState] = useState<PaymentPageState>({ status: "form" });
  const [timeoutMessage, setTimeoutMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const queryClient = useQueryClient();
  const reference = searchParams.get("reference");

  // Restore booking data from localStorage if returning from Paystack
  const savedBookingData = (() => {
    const saved = localStorage.getItem("bookingPaymentData");
    return saved ? JSON.parse(saved) : null;
  })();

  const bookingData = state?.bookingData || savedBookingData;

  // Cancel payment mutation
  const cancelMutation = useMutation({
    mutationFn: async (paymentReference: string) => {
      // First get the payment ID from reference via booking-status
      const statusRes = await apiClient.get<{
        payment_id?: string;
        status?: string;
      }>(`/payments/${paymentReference}/booking-status`);
      const paymentId = statusRes.data?.payment_id;

      if (!paymentId) {
        throw new Error("Payment reference not found");
      }

      const response = await apiClient.post<{
        success: boolean;
        data: {
          payment_id: string;
          reference: string;
          status: string;
          amount: number;
        };
        error?: string;
      }>(`/payments/${paymentId}/cancel`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookingStatus"] });
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      setPageState({
        status: "cancelled",
        reason: "Payment was cancelled by user",
      });
    },
    onError: (err: any) => {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to cancel payment";
      setError(message);
    },
  });

  // Manual verify mutation
  const verifyMutation = useMutation({
    mutationFn: async (paymentReference: string) => {
      const response = await apiClient.get<{
        success: boolean;
        data: {
          payment_id: string;
          reference: string;
          status: string;
          amount: number;
          customer_id?: string;
          invoice_id?: string;
          gateway?: string;
          payment_method?: string;
          created_at?: string;
          updated_at?: string;
        };
        error?: string;
      }>(`/payments/${paymentReference}/verify`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["bookingStatus"] });
      queryClient.invalidateQueries({ queryKey: ["payments"] });

      if (data?.data?.status === "success") {
        setPageState({ status: "success" });
      } else if (data?.data?.status === "cancelled") {
        setPageState({
          status: "cancelled",
          reason: "Payment was cancelled or expired",
        });
      } else if (data?.data?.status === "failed") {
        setPageState({
          status: "failed",
          reason: "Payment could not be verified",
        });
      } else {
        setError(`Payment status: ${data?.data?.status || "unknown"}`);
      }
    },
    onError: (err: any) => {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to verify payment";
      setError(message);
    },
  });

  // Query for booking status - only runs if we have a reference
  const { data: bookingStatus, isLoading: isVerifying } = useQuery({
    queryKey: ["bookingStatus", reference],
    queryFn: async () => {
      const response = await apiClient.get<{
        payment_id?: string;
        reference?: string;
        status?: string;
        appointment_id?: string;
        booking_created?: boolean;
        metadata?: Record<string, any>;
      }>(`/payments/${reference}/booking-status`);
      return response.data;
    },
    enabled: !!reference,
    refetchInterval: 1000,
    refetchIntervalInBackground: true,
    retry: false,
    staleTime: 0,
  });

  // Log booking status changes for debugging
  useEffect(() => {
    if (bookingStatus) {
      console.log("[BookingPayment] booking-status response:", bookingStatus);
    }
  }, [bookingStatus]);

  // Timeout handler: if we've been polling too long with no terminal state,
  // surface a timeout state while keeping polling available via manual verify.
  useEffect(() => {
    if (!reference) return;

    const startedAt = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startedAt;
      const status = bookingStatus?.status;

      if (
        elapsed > PAYMENT_POLL_TIMEOUT_MS &&
        status !== "success" &&
        status !== "cancelled" &&
        status !== "failed"
      ) {
        setTimeoutMessage(
          "This payment session is taking longer than expected. You can cancel it or verify manually.",
        );
      } else {
        setTimeoutMessage(null);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [reference, bookingStatus?.status]);

  // Determine derived page state from backend status
  useEffect(() => {
    if (!bookingStatus) return;

    const status = bookingStatus.status;

    if (status === "cancelled") {
      setPageState({
        status: "cancelled",
        reason: bookingStatus?.metadata?.cancel_reason,
      });
    } else if (status === "failed") {
      setPageState({
        status: "failed",
        reason: bookingStatus?.metadata?.failure_reason,
      });
    } else if (status === "success") {
      // Check if booking creation failed and auto-refund was initiated
      if (bookingStatus?.metadata?.auto_refunded) {
        setPageState({
          status: "refunded",
          reason: bookingStatus?.metadata?.auto_refund_reason || "Booking could not be created. Your payment has been refunded.",
        });
      } else if (bookingStatus?.booking_created) {
        setPageState({ status: "success" });
      }
      // If success but not booking_created and not auto_refunded, keep processing
    }
  }, [bookingStatus]);

  // Query for appointment details - only runs if booking was created
  const { data: appointmentData } = useQuery({
    queryKey: ["appointment", bookingStatus?.appointment_id],
    queryFn: async () => {
      const response = await apiClient.get(
        `/appointments/${bookingStatus?.appointment_id}`,
      );
      return response.data;
    },
    enabled: !!bookingStatus?.appointment_id,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  // Transform appointment data to booking format
  const booking = appointmentData
    ? {
        id: appointmentData.id,
        customerId: appointmentData.customer_id,
        staffId: appointmentData.staff_id,
        serviceId: appointmentData.service_id,
        locationId: appointmentData.location_id,
        startTime: appointmentData.start_time,
        endTime: appointmentData.end_time,
        status: appointmentData.status,
        notes: appointmentData.notes,
        price: appointmentData.price,
        cancellationReason: appointmentData.cancellation_reason,
        cancelledAt: appointmentData.cancelled_at,
        noShowReason: appointmentData.no_show_reason,
        markedNoShowAt: appointmentData.marked_no_show_at,
        confirmedAt: appointmentData.confirmed_at,
        createdAt: appointmentData.created_at,
        updatedAt: appointmentData.updated_at,
      }
    : null;

  // Query for service details
  const { data: serviceData, isLoading: isLoadingService, error: serviceError } = useQuery({
    queryKey: ["service", booking?.serviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/services/${booking?.serviceId}`);
      return response.data;
    },
    enabled: !!booking?.serviceId,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  // Query for staff details
  const { data: staffData, isLoading: isLoadingStaff, error: staffError } = useQuery({
    queryKey: ["staff", booking?.staffId],
    queryFn: async () => {
      const response = await apiClient.get(`/staff/${booking?.staffId}`);
      return response.data;
    },
    enabled: !!booking?.staffId,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const handleInitializePayment = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const callbackUrl = `${window.location.origin}/payments/booking-payment`;

      const response = await apiClient.post("/payments/booking/initialize", {
        amount: formData.amount,
        email: formData.email,
        callback_url: callbackUrl,
        reference: generateSalonReference(),
        metadata: {
          booking_data: bookingData,
          customer_name: bookingData.customerName,
          service_id: bookingData.serviceId,
          staff_id: bookingData.staffId,
        },
      });

      const { authorizationUrl } = response.data;

      localStorage.setItem("bookingPaymentData", JSON.stringify(bookingData));

      if (authorizationUrl) {
        window.location.href = authorizationUrl;
      } else {
        setError("No payment authorization URL received from server");
      }
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to initialize payment. Please try again.";
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelPayment = () => {
    if (!reference) return;
    setError(null);
    cancelMutation.mutate(reference);
  };

  const handleManualVerify = () => {
    if (!reference) return;
    setError(null);
    verifyMutation.mutate(reference);
  };

  const handleRetry = () => {
    setError(null);
    setPageState({ status: "form" });
  };

  const handleConfirmBooking = () => {
    if (booking) {
      localStorage.removeItem("bookingPaymentData");
      navigate("/bookings/confirmation", {
        state: { booking },
      });
    }
  };

  const handleGoToBookings = () => {
    localStorage.removeItem("bookingPaymentData");
    navigate("/bookings");
  };

  const handleTryAgain = () => {
    localStorage.removeItem("bookingPaymentData");
    navigate("/bookings/create");
  };

  // Redirect if no booking data found
  if (!bookingData) {
    navigate("/bookings/create");
    return null;
  }

  // Processing state
  if (pageState.status === "processing" || (isVerifying && pageState.status === "form")) {
    return (
      <div className="min-h-screen bg-background py-8 px-4 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Processing Payment</CardTitle>
            <CardDescription>
              Please wait while we verify your payment...
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-4">
            <Loader2Icon className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Verifying payment and creating booking...
            </p>
            {timeoutMessage && (
              <Alert className="border-warning/20 bg-warning/10">
                <AlertDescription className="text-warning-foreground">
                  {timeoutMessage}
                </AlertDescription>
              </Alert>
            )}
            {reference && (
              <div className="flex flex-col gap-2 w-full">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleManualVerify}
                  disabled={verifyMutation.isPending}
                  className="w-full"
                >
                  {verifyMutation.isPending ? (
                    <>
                      <Loader2Icon size={16} className="mr-2 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    "Verify Payment Manually"
                  )}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleCancelPayment}
                  disabled={cancelMutation.isPending}
                  className="w-full"
                >
                  {cancelMutation.isPending ? "Cancelling..." : "Cancel Payment"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

   // Cancelled state
   if (pageState.status === "cancelled") {
     return (
       <div className="min-h-screen bg-background py-8 px-4 flex items-center justify-center">
         <Card className="w-full max-w-md">
           <CardHeader>
             <CardTitle>Payment Cancelled</CardTitle>
             <CardDescription>
               Your payment was cancelled and no booking was created.
             </CardDescription>
           </CardHeader>
           <CardContent className="space-y-4">
             <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
               <p className="text-sm text-destructive-foreground">
                 {pageState.reason ||
                   "You cancelled the payment or the payment session expired. Your booking has not been created and no charges were made."}
               </p>
             </div>
             <div className="flex flex-col gap-2">
               <Button
                 onClick={handleTryAgain}
                 className="w-full cursor-pointer"
               >
                 Try Again
               </Button>
               <Button
                 variant="outline"
                 onClick={handleGoToBookings}
                 className="w-full cursor-pointer"
               >
                 Back to Bookings
               </Button>
             </div>
           </CardContent>
         </Card>
       </div>
     );
   }

   // Failed state
   if (pageState.status === "failed") {
     return (
       <div className="min-h-screen bg-background py-8 px-4 flex items-center justify-center">
         <Card className="w-full max-w-md">
           <CardHeader>
             <CardTitle>Payment Failed</CardTitle>
             <CardDescription>
               We could not process your payment.
             </CardDescription>
           </CardHeader>
           <CardContent className="space-y-4">
             <div className="bg-warning/10 border border-warning/20 rounded-lg p-4">
               <p className="text-sm text-warning-foreground">
                 {pageState.reason ||
                   "Your payment could not be completed. Please try again or use a different payment method."}
               </p>
             </div>
             <div className="flex flex-col gap-2">
               <Button
                 onClick={handleTryAgain}
                 className="w-full cursor-pointer"
               >
                 Try Again
               </Button>
               <Button
                 variant="outline"
                 onClick={handleGoToBookings}
                 className="w-full cursor-pointer"
               >
                 Back to Bookings
               </Button>
             </div>
           </CardContent>
         </Card>
       </div>
     );
    }

    // Refunded state - booking creation failed but payment was refunded
    if (pageState.status === "refunded") {
      return (
        <div className="min-h-screen bg-background py-8 px-4 flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Booking Could Not Be Created</CardTitle>
              <CardDescription>
                We were unable to create your booking, but your payment has been refunded.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-warning/10 border border-warning/20 rounded-lg p-4">
                <p className="text-sm text-warning-foreground">
                  {pageState.reason ||
                    "Your booking could not be completed. The payment has been automatically refunded to your original payment method. This usually takes 1-3 business days to reflect."}
                </p>
              </div>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={handleTryAgain}
                  className="w-full cursor-pointer"
                >
                  Try Again
                </Button>
                <Button
                  variant="outline"
                  onClick={handleGoToBookings}
                  className="w-full cursor-pointer"
                >
                  Back to Bookings
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    // Success / booking confirmation state
    if (booking && bookingStatus?.booking_created) {
     const bookingDate = new Date(booking.startTime);
     const bookingRef = booking.id.slice(-8).toUpperCase();

     return (
       <div className="min-h-screen bg-background flex items-center justify-center p-4">
         <Card className="w-full max-w-md shadow-lg">
           <div className="p-8 text-center space-y-6">
             <div className="flex justify-center">
               <div className="relative">
                 <div className="absolute inset-0 bg-success/20 rounded-full animate-pulse" />
                 <CheckCircleIcon
                   size={64}
                   className="text-success relative z-10"
                 />
               </div>
             </div>

             <div>
               <h1 className="text-2xl font-bold text-foreground mb-2">
                 Booking Confirmed!
               </h1>
               <p className="text-muted-foreground">
                 Your appointment has been successfully scheduled.
               </p>
             </div>

             <div className="bg-muted rounded-lg p-4 border border-border">
               <p className="text-xs text-muted-foreground mb-1">
                 Booking Reference
               </p>
               <p className="text-lg font-mono font-bold text-foreground">
                 {bookingRef}
               </p>
             </div>

              <div className="space-y-3 text-left bg-muted rounded-lg p-4">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Customer</span>
                  <span className="text-sm font-semibold text-foreground">
                    {bookingData?.customerName || "N/A"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Service</span>
                  <span className="text-sm font-semibold text-foreground">
                    {isLoadingService ? (
                      <Loader2Icon size={14} className="animate-spin" />
                    ) : serviceError || !serviceData?.name ? (
                      <span className="text-warning">Service no longer available</span>
                    ) : (
                      serviceData.name
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Staff</span>
                  <span className="text-sm font-semibold text-foreground">
                    {isLoadingStaff ? (
                      <Loader2Icon size={14} className="animate-spin" />
                    ) : staffError || (!staffData?.firstName && !staffData?.lastName) ? (
                      <span className="text-warning">Staff no longer available</span>
                    ) : staffData?.status === "terminated" ? (
                      <span className="text-warning">
                        {staffData.firstName} {staffData.lastName} (no longer active)
                      </span>
                    ) : (
                      `${staffData.firstName} ${staffData.lastName}`
                    )}
                  </span>
                </div>
               <div className="flex justify-between">
                 <span className="text-sm text-muted-foreground">Price</span>
                 <span className="text-sm font-semibold text-foreground">
                   ₦{booking?.price?.toLocaleString() || "0"}
                 </span>
               </div>
               <div className="border-t border-border pt-3">
                 <div className="flex justify-between">
                   <span className="text-sm text-muted-foreground">Date</span>
                   <span className="text-sm font-semibold text-foreground">
                     {bookingDate.toLocaleDateString("en-US", {
                       weekday: "long",
                       year: "numeric",
                       month: "long",
                       day: "numeric",
                     })}
                   </span>
                 </div>
               </div>
               <div className="flex justify-between">
                 <span className="text-sm text-muted-foreground">Time</span>
                 <span className="text-sm font-semibold text-foreground">
                   {bookingDate.toLocaleTimeString("en-US", {
                     hour: "2-digit",
                     minute: "2-digit",
                   })}
                 </span>
               </div>
               <div className="flex justify-between">
                 <span className="text-sm text-muted-foreground">Status</span>
                 <span className="text-sm font-semibold text-success">
                   {booking.status.charAt(0).toUpperCase() +
                     booking.status.slice(1)}
                 </span>
               </div>
             </div>

             <div className="bg-warning/10 rounded-lg p-4 border border-warning/20">
               <p className="text-xs font-semibold text-warning-foreground mb-2">
                 Next Steps
               </p>
               <ul className="text-xs text-warning-foreground/90 space-y-1">
                 <li>• Check your email for confirmation details</li>
                 <li>• Arrive 5-10 minutes early</li>
                 <li>• You can reschedule anytime from your bookings</li>
               </ul>
             </div>

             <div className="flex flex-col gap-3 pt-4">
               <Button
                 onClick={handleConfirmBooking}
                 className="w-full cursor-pointer"
               >
                 View Booking Details
               </Button>
               <Button
                 variant="outline"
                 onClick={handleGoToBookings}
                 className="w-full cursor-pointer"
               >
                 Back to Bookings
               </Button>
             </div>
           </div>
         </Card>
       </div>
     );
   }

  // Payment form / main page
  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Complete Payment</h1>
          <p className="text-muted-foreground mt-2">
            Secure your booking by completing the payment
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Booking Summary */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Booking Details</CardTitle>
                <CardDescription>
                  Review your booking information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {bookingData ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">
                          Customer Name
                        </span>
                        <span className="font-medium">
                          {bookingData.customerName}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">
                          Email
                        </span>
                        <span className="font-medium">
                          {bookingData.customerEmail}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">
                          Phone
                        </span>
                        <span className="font-medium">
                          {bookingData.customerPhone}
                        </span>
                      </div>
                      <div className="border-t pt-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">
                            Appointment Date
                          </span>
                          <span className="font-medium">
                            {new Date(bookingData.startTime).toLocaleDateString(
                              "en-US",
                              {
                                weekday: "short",
                                year: "numeric",
                                month: "short",
                                day: "numeric",
                              },
                            )}
                          </span>
                        </div>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">
                          Time
                        </span>
                        <span className="font-medium">
                          {bookingData.startTime.split("T")[1]?.slice(0, 5)}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      Loading booking information...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Payment Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Payment</CardTitle>
                <CardDescription>Amount to pay</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleInitializePayment} className="space-y-4">
                  <div>
                    <Label htmlFor="amount" className="text-base font-semibold">
                      Total Amount
                    </Label>
                    <div className="text-3xl font-bold text-primary mt-2">
                      ₦{formData.amount.toLocaleString()}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    disabled={isSubmitting}
                    required
                  />
                  </div>

                  {error && (
                    <Alert className="border-destructive/20 bg-destructive/10">
                      <AlertCircleIcon size={16} className="text-destructive" />
                      <AlertDescription className="text-destructive-foreground">
                        {error}
                      </AlertDescription>
                    </Alert>
                  )}

                  <Button type="submit" disabled={isSubmitting} className="w-full">
                    {isSubmitting ? (
                      <>
                        <Loader2Icon size={16} className="mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      "Pay Now"
                    )}
                  </Button>

                  {error && (
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={handleRetry}
                    >
                      Retry
                    </Button>
                  )}

                  <Button
                    type="button"
                    variant="ghost"
                    className="w-full"
                    onClick={() => navigate("/bookings/create")}
                  >
                    Cancel
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex gap-3">
          <LockIcon size={20} className="text-primary flex-shrink-0 mt-0.5" />
          <p className="text-sm text-foreground">
            Your payment is secure and encrypted. We use Paystack to process
            payments safely.
          </p>
        </div>
      </div>
    </div>
  );
}
