import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Booking } from "@/types";
import { formatTime } from "@/lib/utils/format";

interface DayViewProps {
  date: Date;
  bookings: Booking[];
  onBookingClick?: (bookingId: string) => void;
  isLoading?: boolean;
}

export function DayView({
  date,
  bookings,
  onBookingClick,
  isLoading = false,
}: DayViewProps) {
  const hours = Array.from({ length: 24 }, (_, i) => i);

  const bookingsByHour = useMemo(() => {
    const map = new Map<number, Booking[]>();
    bookings.forEach((booking) => {
      const startHour = new Date(booking.startTime).getHours();
      if (!map.has(startHour)) {
        map.set(startHour, []);
      }
      map.get(startHour)?.push(booking);
    });
    return map;
  }, [bookings]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "bg-success/10 border-success/30";
      case "scheduled":
        return "bg-primary/10 border-primary/30";
      case "completed":
        return "bg-muted border-border";
      case "cancelled":
        return "bg-destructive/10 border-destructive/30";
      default:
        return "bg-warning/10 border-warning/30";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-6 w-48 mb-4" />
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {hours.slice(0, 12).map((hour) => (
            <div key={hour} className="flex gap-2">
              <div className="w-16 text-xs text-muted-foreground text-right pt-2">
                <Skeleton className="h-4 w-12" />
              </div>
              <div className="flex-1 min-h-12 border-l border-border pl-2">
                <Skeleton className="h-8 w-full mb-1" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold text-foreground mb-4">
        {date.toLocaleDateString("en-US", {
          weekday: "long",
          month: "long",
          day: "numeric",
        })}
      </div>

      <div className="space-y-1 max-h-96 overflow-y-auto">
        {hours.map((hour) => (
          <div key={hour} className="flex gap-2">
            <div className="w-16 text-xs text-muted-foreground text-right pt-2">
              {String(hour).padStart(2, "0")}:00
            </div>
            <div className="flex-1 min-h-12 border-l border-border pl-2">
              {bookingsByHour.get(hour)?.map((booking) => (
                <Button
                  key={booking.id}
                  variant="outline"
                  size="sm"
                  onClick={() => onBookingClick?.(booking.id)}
                  className={`w-full text-left text-xs mb-1 ${getStatusColor(
                    booking.status,
                  )}`}
                >
                  <div className="truncate">
                    {formatTime(new Date(booking.startTime))} - Customer
                  </div>
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
