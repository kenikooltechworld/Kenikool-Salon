import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookingCardSkeleton } from "@/components/ui/skeleton";
import {
  CalendarIcon,
  UserIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

interface Booking {
  id: string;
  client_name: string;
  client_id: string;
  stylist_name: string;
  booking_date: string;
  status: string;
  service_price: number;
  variant_name?: string;
}

interface RecentBookingsListProps {
  serviceId: string;
}

export function RecentBookingsList({ serviceId }: RecentBookingsListProps) {
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading } = useQuery({
    queryKey: ["service-bookings", serviceId, page],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/bookings`,
        {
          params: { page, limit },
        }
      );
      return response.data;
    },
  });

  const bookings: Booking[] = data?.bookings || [];
  const totalPages = Math.ceil((data?.total || 0) / limit);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "confirmed":
        return "primary";
      case "pending":
        return "warning";
      case "cancelled":
        return "error";
      default:
        return "secondary";
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <Card className="p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
          Recent Bookings
        </h2>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <BookingCardSkeleton key={i} />
          ))}
        </div>
      </Card>
    );
  }

  if (bookings.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Recent Bookings
        </h2>
        <div className="text-center py-8">
          <CalendarIcon
            size={48}
            className="mx-auto text-muted-foreground mb-4"
          />
          <p className="text-muted-foreground">No bookings yet</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6 animate-fade-in">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Recent Bookings
      </h2>

      <div className="space-y-3">
        {bookings.map((booking, index) => (
          <div
            key={booking.id}
            className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 sm:p-4 border border-border rounded-lg hover:bg-muted/50 hover:shadow-md transition-all duration-200 cursor-pointer animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
            onClick={() => {
              // Navigate to booking details
              window.location.href = `/dashboard/bookings?id=${booking.id}`;
            }}
          >
            <div className="flex items-center gap-3 sm:gap-4 flex-1 mb-3 sm:mb-0">
              <div className="p-2 bg-primary/10 rounded-lg shrink-0">
                <UserIcon size={18} className="sm:w-5 sm:h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm sm:text-base text-foreground truncate">
                  {booking.client_name}
                </p>
                <p className="text-xs sm:text-sm text-muted-foreground truncate">
                  with {booking.stylist_name}
                  {booking.variant_name && ` • ${booking.variant_name}`}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-3 sm:gap-4">
              <div className="text-left sm:text-right">
                <p className="text-xs sm:text-sm font-medium text-foreground">
                  {formatDate(booking.booking_date)}
                </p>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  ₦{booking.service_price.toLocaleString()}
                </p>
              </div>
              <Badge
                variant={
                  getStatusColor(booking.status) as
                    | "success"
                    | "primary"
                    | "warning"
                    | "error"
                    | "secondary"
                }
                className="text-xs"
              >
                {booking.status}
              </Badge>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-6 pt-4 border-t border-border">
          <p className="text-xs sm:text-sm text-muted-foreground text-center sm:text-left">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2 justify-center sm:justify-end">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="text-xs sm:text-sm"
            >
              <ChevronLeftIcon size={14} className="sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Previous</span>
              <span className="sm:hidden">Prev</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="text-xs sm:text-sm"
            >
              <span className="hidden sm:inline">Next</span>
              <span className="sm:hidden">Next</span>
              <ChevronRightIcon size={14} className="sm:w-4 sm:h-4" />
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
