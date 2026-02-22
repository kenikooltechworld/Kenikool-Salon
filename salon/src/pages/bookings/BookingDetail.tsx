import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBooking } from "@/hooks/useBookings";
import { BookingStatusBadge } from "@/components/bookings/BookingStatusBadge";
import { formatDate, formatTime, formatCurrency } from "@/lib/utils/format";
import { XIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface BookingDetailProps {
  bookingId: string;
  onClose?: () => void;
  onConfirm?: (id: string) => void;
  onCancel?: (id: string) => void;
  onComplete?: (id: string) => void;
  onMarkNoShow?: (id: string) => void;
}

export function BookingDetail({
  bookingId,
  onClose,
  onConfirm,
  onCancel,
  onComplete,
  onMarkNoShow,
}: BookingDetailProps) {
  const { data: booking, isLoading } = useBooking(bookingId);

  // Fetch service details
  const { data: serviceData, isLoading: isLoadingService } = useQuery({
    queryKey: ["service", booking?.serviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/services/${booking?.serviceId}`);
      return response.data;
    },
    enabled: !!booking?.serviceId,
    retry: false,
  });

  // Fetch staff details
  const { data: staffData, isLoading: isLoadingStaff } = useQuery({
    queryKey: ["staff", booking?.staffId],
    queryFn: async () => {
      const response = await apiClient.get(`/staff/${booking?.staffId}`);
      return response.data;
    },
    enabled: !!booking?.staffId,
    retry: false,
  });

  // Fetch customer details
  const { data: customerData, isLoading: isLoadingCustomer } = useQuery({
    queryKey: ["customer", booking?.customerId],
    queryFn: async () => {
      const response = await apiClient.get(`/customers/${booking?.customerId}`);
      return response.data;
    },
    enabled: !!booking?.customerId,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="w-full max-w-md">
          {/* Header Skeleton */}
          <div className="flex items-center justify-between border-b border-border p-4 sticky top-0 bg-background">
            <Skeleton className="h-6 w-40" />
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="cursor-pointer flex-shrink-0 ml-2"
            >
              <XIcon size={20} />
            </Button>
          </div>

          {/* Content Skeleton */}
          <div className="space-y-4 p-4 overflow-y-auto max-h-[calc(100vh-200px)]">
            {/* Status */}
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-6 w-24 rounded-full" />
            </div>

            {/* Customer */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-32" />
            </div>

            {/* Service */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-40" />
            </div>

            {/* Staff */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-5 w-36" />
            </div>

            {/* Price */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-5 w-28" />
            </div>

            {/* Booking ID */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-48" />
            </div>

            {/* Date */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-5 w-40" />
            </div>

            {/* Times */}
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

            {/* Timestamps */}
            <div className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>

          {/* Actions Skeleton */}
          <div className="flex flex-wrap gap-2 border-t border-border p-4">
            <Skeleton className="flex-1 min-w-[100px] h-10" />
            <Skeleton className="flex-1 min-w-[100px] h-10" />
          </div>
        </Card>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md p-6">
          <div className="text-center py-8 text-muted-foreground">
            Booking not found
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <Card className="w-full max-w-md my-8">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border p-4 sticky top-0 bg-background">
          <h2 className="text-lg font-bold text-foreground truncate">
            Booking Details
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="cursor-pointer flex-shrink-0 ml-2"
          >
            <XIcon size={20} />
          </Button>
        </div>

        {/* Content */}
        <div className="space-y-3 p-4 overflow-y-auto max-h-[calc(100vh-200px)]">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Status</span>
            <BookingStatusBadge status={booking.status} />
          </div>

          <div>
            <span className="text-muted-foreground">Customer</span>
            <p className="text-foreground">
              {isLoadingCustomer ? (
                <Skeleton className="h-5 w-32 mt-1" />
              ) : customerData?.first_name && customerData?.last_name ? (
                `${customerData.first_name} ${customerData.last_name}`
              ) : (
                "N/A"
              )}
            </p>
          </div>

          <div>
            <span className="text-muted-foreground">Service</span>
            <p className="text-foreground">
              {isLoadingService ? (
                <Skeleton className="h-5 w-40 mt-1" />
              ) : (
                serviceData?.name || "N/A"
              )}
            </p>
          </div>

          <div>
            <span className="text-muted-foreground">Staff</span>
            <p className="text-foreground">
              {isLoadingStaff ? (
                <Skeleton className="h-5 w-36 mt-1" />
              ) : staffData?.firstName && staffData?.lastName ? (
                `${staffData.firstName} ${staffData.lastName}`
              ) : (
                "N/A"
              )}
            </p>
          </div>

          <div>
            <span className="text-muted-foreground">Price</span>
            <p className="text-foreground font-semibold">
              {booking?.price ? formatCurrency(booking.price, "NGN") : "N/A"}
            </p>
          </div>

          <div>
            <span className="text-muted-foreground">Booking ID</span>
            <p className="font-mono text-sm text-foreground">{booking.id}</p>
          </div>

          <div>
            <span className="text-muted-foreground">Date</span>
            <p className="text-foreground">
              {formatDate(new Date(booking.startTime))}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-muted-foreground">Start Time</span>
              <p className="text-foreground">
                {formatTime(new Date(booking.startTime))}
              </p>
            </div>
            <div>
              <span className="text-muted-foreground">End Time</span>
              <p className="text-foreground">
                {formatTime(new Date(booking.endTime))}
              </p>
            </div>
          </div>

          {booking.notes && (
            <div>
              <span className="text-muted-foreground">Notes</span>
              <p className="text-foreground">{booking.notes}</p>
            </div>
          )}

          <div className="text-xs text-muted-foreground">
            <p>Created: {formatDate(new Date(booking.createdAt))}</p>
            <p>Updated: {formatDate(new Date(booking.updatedAt))}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 border-t border-border p-4">
          {booking.status === "scheduled" && onConfirm && (
            <Button
              variant="primary"
              className="flex-1 min-w-[100px] cursor-pointer"
              onClick={() => {
                onConfirm(booking.id);
                onClose?.();
              }}
            >
              Confirm
            </Button>
          )}
          {booking.status === "confirmed" && onComplete && (
            <Button
              variant="primary"
              className="flex-1 min-w-[100px] cursor-pointer"
              onClick={() => {
                onComplete(booking.id);
                onClose?.();
              }}
            >
              Complete
            </Button>
          )}
          {(booking.status === "scheduled" || booking.status === "confirmed") &&
            onCancel && (
              <Button
                variant="destructive"
                className="flex-1 min-w-[100px] cursor-pointer"
                onClick={() => {
                  onCancel(booking.id);
                  onClose?.();
                }}
              >
                Cancel
              </Button>
            )}
          {booking.status === "confirmed" && onMarkNoShow && (
            <Button
              variant="outline"
              className="flex-1 min-w-[100px] cursor-pointer"
              onClick={() => {
                onMarkNoShow(booking.id);
                onClose?.();
              }}
            >
              No-Show
            </Button>
          )}
          <Button
            variant="outline"
            className="flex-1 min-w-[100px] cursor-pointer"
            onClick={onClose}
          >
            Close
          </Button>
        </div>
      </Card>
    </div>
  );
}
