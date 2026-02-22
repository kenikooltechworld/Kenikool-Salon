import { useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Booking } from "@/types";
import { formatTime } from "@/lib/utils/format";

interface WeekViewProps {
  startDate: Date;
  bookings: Booking[];
  onBookingClick?: (bookingId: string) => void;
  isLoading?: boolean;
}

export function WeekView({
  startDate,
  bookings,
  onBookingClick,
  isLoading = false,
}: WeekViewProps) {
  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const weekDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      days.push(date);
    }
    return days;
  }, [startDate]);

  const bookingsByDay = useMemo(() => {
    const map = new Map<string, Booking[]>();
    bookings.forEach((booking) => {
      const dateKey = getLocalDateString(new Date(booking.startTime));
      if (!map.has(dateKey)) {
        map.set(dateKey, []);
      }
      map.get(dateKey)?.push(booking);
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
      <div className="space-y-4">
        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Card key={i} className="p-3 min-h-32">
              <Skeleton className="h-4 w-16 mb-2" />
              <div className="space-y-1">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-7 gap-2">
        {weekDays.map((day) => {
          const dateKey = getLocalDateString(day);
          const dayBookings = bookingsByDay.get(dateKey) || [];

          return (
            <Card key={dateKey} className="p-3 min-h-32">
              <div className="text-xs font-semibold text-foreground mb-2">
                {day.toLocaleDateString("en-US", {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                })}
              </div>
              <div className="space-y-1">
                {dayBookings.length > 0 ? (
                  dayBookings.map((booking) => (
                    <Button
                      key={booking.id}
                      variant="outline"
                      size="sm"
                      onClick={() => onBookingClick?.(booking.id)}
                      className={`w-full text-left text-xs truncate ${getStatusColor(
                        booking.status,
                      )}`}
                    >
                      {formatTime(new Date(booking.startTime))}
                    </Button>
                  ))
                ) : (
                  <div className="text-xs text-muted-foreground text-center py-2">
                    No bookings
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
