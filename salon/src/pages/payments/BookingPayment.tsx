import { useState, type FormEvent } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
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

export function BookingPayment() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const state = location.state as BookingPaymentState;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore booking data from localStorage if returning from Paystack
  const savedBookingData = (() => {
    const saved = localStorage.getItem("bookingPaymentData");
    return saved ? JSON.parse(saved) : null;
  })();

  const bookingDataForForm = state?.bookingData || savedBookingData;

  const [formData, setFormData] = useState({
    email: bookingDataForForm?.customerEmail || "",
    amount: state?.amount || 0,
  });

  // Get reference from URL params
  const reference = searchParams.get("reference");

  // Use booking data from state or localStorage
  const bookingData = bookingDataForForm;

  // Query for booking status - only runs if we have a reference
  const { data: bookingStatus, isLoading: isVerifying } = useQuery({
    queryKey: ["bookingStatus", reference],
    queryFn: async () => {
      const response = await apiClient.get(
        `/payments/${reference}/booking-status`,
      );
      return response.data;
    },
    enabled: !!reference, // Only run if reference exists
    refetchInterval: 1000, // Poll every 1 second
    refetchIntervalInBackground: true,
    retry: false, // Don't retry on 404, just keep polling
    staleTime: 0, // Always consider data stale
  });

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
  const { data: serviceData, isLoading: isLoadingService } = useQuery({
    queryKey: ["service", booking?.serviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/services/${booking?.serviceId}`);
      return response.data;
    },
    enabled: !!booking?.serviceId,
    retry: false,
  });

  // Query for staff details
  const { data: staffData, isLoading: isLoadingStaff } = useQuery({
    queryKey: ["staff", booking?.staffId],
    queryFn: async () => {
      const response = await apiClient.get(`/staff/${booking?.staffId}`);
      return response.data;
    },
    enabled: !!booking?.staffId,
    retry: false,
  });

  const handleInitializePayment = async (e: FormEvent<HTMLFormElement>) => {
    console.log("[BookingPayment] Form submitted");
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log("[BookingPayment] Initializing payment with:", {
        amount: formData.amount,
        email: formData.email,
      });

      // Get the callback URL - where Paystack should redirect after payment
      const callbackUrl = `${window.location.origin}/payments/booking-payment`;

      // Initialize payment with Paystack using booking payment endpoint
      const response = await apiClient.post("/payments/booking/initialize", {
        amount: formData.amount,
        email: formData.email,
        callback_url: callbackUrl,
        metadata: {
          booking_data: bookingData,
          customer_name: bookingData.customerName,
          service_id: bookingData.serviceId,
          staff_id: bookingData.staffId,
        },
      });

      console.log(
        "[BookingPayment] Payment initialized successfully:",
        response.data,
      );

      const { authorization_url } = response.data;

      // Save booking data to localStorage before redirecting to Paystack
      localStorage.setItem("bookingPaymentData", JSON.stringify(bookingData));
      console.log("[BookingPayment] Saved booking data to localStorage");

      // Redirect to Paystack payment page
      if (authorization_url) {
        console.log(
          "[BookingPayment] Redirecting to Paystack:",
          authorization_url,
        );
        window.location.href = authorization_url;
      } else {
        setError("No payment authorization URL received from server");
      }
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to initialize payment. Please try again.";
      setError(errorMessage);
      console.error("[BookingPayment] Error:", {
        message: errorMessage,
        status: err?.response?.status,
        data: err?.response?.data,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
  };

  const handleConfirmBooking = () => {
    if (booking) {
      console.log(
        "[BookingPayment] User confirmed booking, clearing localStorage and navigating",
      );
      // Clear localStorage now that user has confirmed
      localStorage.removeItem("bookingPaymentData");
      // Navigate to confirmation page
      navigate("/bookings/confirmation", {
        state: { booking },
      });
    }
  };

  // Redirect if no booking data found
  if (!bookingData) {
    console.warn(
      "[BookingPayment] No booking data found, redirecting to create booking",
    );
    navigate("/bookings/create");
    return null;
  }

  // Show loading state while verifying payment
  if (isVerifying) {
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
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show booking confirmation on same page after successful payment
  if (booking && bookingStatus?.booking_created) {
    const bookingDate = new Date(booking.startTime);
    const bookingRef = booking.id.slice(-8).toUpperCase();

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-lg">
          <div className="p-8 text-center space-y-6">
            {/* Success Icon */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-green-100 rounded-full animate-pulse" />
                <CheckCircleIcon
                  size={64}
                  className="text-green-600 relative z-10"
                />
              </div>
            </div>

            {/* Success Message */}
            <div>
              <h1 className="text-2xl font-bold text-foreground mb-2">
                Booking Confirmed!
              </h1>
              <p className="text-muted-foreground">
                Your appointment has been successfully scheduled.
              </p>
            </div>

            {/* Booking Reference */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-xs text-muted-foreground mb-1">
                Booking Reference
              </p>
              <p className="text-lg font-mono font-bold text-foreground">
                {bookingRef}
              </p>
            </div>

            {/* Booking Details */}
            <div className="space-y-3 text-left bg-gray-50 rounded-lg p-4">
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
                  ) : (
                    serviceData?.name || "N/A"
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Staff</span>
                <span className="text-sm font-semibold text-foreground">
                  {isLoadingStaff ? (
                    <Loader2Icon size={14} className="animate-spin" />
                  ) : staffData?.firstName && staffData?.lastName ? (
                    `${staffData.firstName} ${staffData.lastName}`
                  ) : (
                    "N/A"
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Price</span>
                <span className="text-sm font-semibold text-foreground">
                  ₦{booking?.price?.toLocaleString() || "0"}
                </span>
              </div>
              <div className="border-t pt-3">
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
                <span className="text-sm font-semibold text-green-600">
                  {booking.status.charAt(0).toUpperCase() +
                    booking.status.slice(1)}
                </span>
              </div>
            </div>

            {/* Next Steps */}
            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
              <p className="text-xs font-semibold text-amber-900 mb-2">
                Next Steps
              </p>
              <ul className="text-xs text-amber-800 space-y-1">
                <li>• Check your email for confirmation details</li>
                <li>• Arrive 5-10 minutes early</li>
                <li>• You can reschedule anytime from your bookings</li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col gap-3 pt-4">
              <Button
                onClick={handleConfirmBooking}
                className="w-full cursor-pointer"
              >
                View Booking Details
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate("/bookings")}
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
                      disabled={loading}
                      required
                    />
                  </div>

                  {error && (
                    <Alert className="border-red-200 bg-red-50">
                      <AlertCircleIcon size={16} className="text-red-600" />
                      <AlertDescription className="text-red-800">
                        {error}
                      </AlertDescription>
                    </Alert>
                  )}

                  <Button type="submit" disabled={loading} className="w-full">
                    {loading ? (
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
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg flex gap-3">
          <LockIcon size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-900">
            Your payment is secure and encrypted. We use Paystack to process
            payments safely.
          </p>
        </div>
      </div>
    </div>
  );
}
