import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBooking } from "@/hooks/useBookings";
import { useConfirmBooking, useCancelBooking, useCompleteBooking, useMarkNoShow } from "@/hooks/useBookings";
import { BookingStatusBadge } from "@/components/bookings/BookingStatusBadge";
import { formatDate, formatTime, formatCurrency } from "@/lib/utils/format";
import { ArrowLeftIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useToast } from "@/components/ui/toast";

export default function BookingDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const bookingId = id || "";
  const { showToast } = useToast();
  const { mutate: confirmBooking } = useConfirmBooking();
  const { mutate: cancelBooking } = useCancelBooking();
  const { mutate: completeBooking } = useCompleteBooking();
  const { mutate: markNoShow } = useMarkNoShow();

  const { data: booking, isLoading } = useBooking(bookingId, { refetchOnMount: true });
  console.log("[BookingDetail] booking data:", booking);

  const { data: detail, isLoading: isLoadingDetail } = useQuery({
    queryKey: ["bookingDetail", bookingId],
    queryFn: async () => {
      const response = await apiClient.get(`/appointments/${bookingId}/detail`);
      return response.data;
    },
    enabled: !!bookingId,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });

  const serviceData = detail?.service || null;
  const staffData = detail?.staff || null;
  const customerData = detail?.customer || null;

  if (isLoading || isLoadingDetail) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/bookings")}
            className="cursor-pointer"
          >
            <ArrowLeftIcon size={16} />
            Back to Bookings
          </Button>
        </div>
        <Card className="p-6 space-y-4">
          <Skeleton className="h-6 w-40" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-5 w-32" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-5 w-40" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-5 w-36" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-5 w-28" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-5 w-48" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-5 w-40" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-24" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-24" />
            </div>
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-32" />
          </div>
        </Card>
      </div>
    );
  }

  if (!booking || !booking.startTime) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/bookings")}
            className="cursor-pointer"
          >
            <ArrowLeftIcon size={16} />
            Back to Bookings
          </Button>
        </div>
        <Card className="p-6">
          <div className="text-center py-8 text-muted-foreground">
            Booking not found
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/bookings")}
          className="cursor-pointer"
        >
          <ArrowLeftIcon size={16} />
          Back to Bookings
        </Button>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-foreground">Booking Details</h1>
            <BookingStatusBadge status={booking.status} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Customer</span>
              {!customerData ? (
                <Skeleton className="h-5 w-32 mt-1" />
              ) : customerData?.first_name && customerData?.last_name ? (
                <p className="text-foreground font-medium">{customerData.first_name} {customerData.last_name}</p>
              ) : (
                <p className="text-foreground">N/A</p>
              )}
            </div>

            <div>
              <span className="text-sm text-muted-foreground">Service</span>
              {!serviceData ? (
                <Skeleton className="h-5 w-40 mt-1" />
              ) : (
                <p className="text-foreground font-medium">{serviceData?.name || "N/A"}</p>
              )}
            </div>

            <div>
              <span className="text-sm text-muted-foreground">Staff</span>
              {!staffData ? (
                <Skeleton className="h-5 w-36 mt-1" />
              ) : staffData?.first_name && staffData?.last_name ? (
                <p className="text-foreground font-medium">{staffData.first_name} {staffData.last_name}</p>
              ) : (
                <p className="text-foreground">N/A</p>
              )}
            </div>

            <div>
              <span className="text-sm text-muted-foreground">Price</span>
              <p className="text-foreground font-semibold">
                {booking?.price ? formatCurrency(booking.price, "NGN") : "N/A"}
              </p>
            </div>

            {booking.locationId && (
              <div>
                <span className="text-sm text-muted-foreground">Location</span>
                <p className="text-foreground">{booking.locationId}</p>
              </div>
            )}

            <div>
              <span className="text-sm text-muted-foreground">Booking ID</span>
              <p className="font-mono text-sm text-foreground">{booking.id}</p>
            </div>

            <div>
              <span className="text-sm text-muted-foreground">Date</span>
              <p className="text-foreground">
                {formatDate(new Date(booking.startTime))}
              </p>
            </div>

            <div>
              <span className="text-sm text-muted-foreground">Start Time</span>
              <p className="text-foreground">
                {formatTime(new Date(booking.startTime))}
              </p>
            </div>

            <div>
              <span className="text-sm text-muted-foreground">End Time</span>
              <p className="text-foreground">
                {formatTime(new Date(booking.endTime))}
              </p>
            </div>
          </div>

          {booking.notes && (
            <div>
              <span className="text-sm text-muted-foreground">Notes</span>
              <p className="text-foreground">{booking.notes}</p>
            </div>
          )}

          <div className="text-xs text-muted-foreground">
            <p>Created: {formatDate(new Date(booking.createdAt))}</p>
            <p>Updated: {formatDate(new Date(booking.updatedAt))}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 border-t border-border pt-4 mt-4">
          {booking.status === "scheduled" && (
            <Button
              variant="primary"
              className="cursor-pointer"
              onClick={() => {
                confirmBooking(booking.id, {
                  onSuccess: () => {
                    showToast({
                      title: "Success",
                      description: "Appointment confirmed successfully",
                      variant: "success",
                    });
                  },
                  onError: () => {
                    showToast({
                      title: "Error",
                      description: "Failed to confirm appointment",
                      variant: "error",
                    });
                  },
                });
              }}
            >
              Confirm
            </Button>
          )}
          {booking.status === "confirmed" && (
            <Button
              variant="primary"
              className="cursor-pointer"
              onClick={() => {
                completeBooking(booking.id, {
                  onSuccess: () => {
                    showToast({
                      title: "Success",
                      description: "Appointment completed successfully",
                      variant: "success",
                    });
                  },
                  onError: () => {
                    showToast({
                      title: "Error",
                      description: "Failed to complete appointment",
                      variant: "error",
                    });
                  },
                });
              }}
            >
              Complete
            </Button>
          )}
          {(booking.status === "scheduled" || booking.status === "confirmed") && (
            <Button
              variant="destructive"
              className="cursor-pointer"
              onClick={() => {
                cancelBooking(booking.id, {
                  onSuccess: () => {
                    showToast({
                      title: "Success",
                      description: "Appointment cancelled successfully",
                      variant: "success",
                    });
                    navigate("/bookings");
                  },
                  onError: () => {
                    showToast({
                      title: "Error",
                      description: "Failed to cancel appointment",
                      variant: "error",
                    });
                  },
                });
              }}
            >
              Cancel
            </Button>
          )}
          {(booking.status === "scheduled" || booking.status === "confirmed") && (
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={() => {
                markNoShow({ id: booking.id, reason: "" }, {
                  onSuccess: () => {
                    showToast({
                      title: "Success",
                      description: "Marked as no-show successfully",
                      variant: "success",
                    });
                  },
                  onError: () => {
                    showToast({
                      title: "Error",
                      description: "Failed to mark as no-show",
                      variant: "error",
                    });
                  },
                });
              }}
            >
              No-Show
            </Button>
          )}
          {booking.status === "completed" &&
            booking.paymentOption === "later" &&
            booking.paymentStatus !== "completed" ? (
              <Button
                variant="primary"
                className="cursor-pointer bg-green-600 hover:bg-green-700"
                onClick={() => navigate("/pos", { state: { bookingId: booking.id, booking } })}
              >
                Collect Payment
              </Button>
            ) : (
              <span className="text-xs text-muted-foreground">
                {`Collect payment hidden: status=${booking.status}, paymentOption=${booking.paymentOption}, paymentStatus=${booking.paymentStatus}`}
              </span>
            )}
          <Button
            variant="outline"
            className="cursor-pointer"
            onClick={() => navigate("/bookings")}
          >
            Close
          </Button>
        </div>
      </Card>
    </div>
  );
}
