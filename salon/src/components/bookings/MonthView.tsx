import { useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatTime } from "@/lib/utils/format";
import type { Booking } from "@/types";

interface MonthViewProps {
  date: Date;
  bookings: Booking[];
  onBookingClick?: (bookingId: string) => void;
  isLoading?: boolean;
}

export function MonthView({
  date,
  bookings,
  onBookingClick,
  isLoading = false,
}: MonthViewProps) {
  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (dateObj: Date) => {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, "0");
    const day = String(dateObj.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const monthDays = useMemo(() => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    return days;
  }, [date]);

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

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={`header-${i}`} className="h-8 w-full" />
          ))}
          {Array.from({ length: 35 }).map((_, i) => (
            <Card
              key={i}
              className="p-2 min-h-20 flex flex-col justify-between"
            >
              <Skeleton className="h-4 w-6 mb-2" />
              <div className="space-y-1">
                <Skeleton className="h-6 w-full" />
                <Skeleton className="h-6 w-full" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-lg font-semibold text-foreground">
        {date.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {weekDays.map((day) => (
          <div
            key={day}
            className="text-center text-xs font-semibold text-muted-foreground py-2"
          >
            {day}
          </div>
        ))}

        {monthDays.map((day, index) => {
          const dateKey = day ? getLocalDateString(day) : null;
          const dayBookings = dateKey ? bookingsByDay.get(dateKey) || [] : [];
          const count = dayBookings.length;

          return (
            <Card
              key={index}
              className="p-2 min-h-20 flex flex-col justify-between"
            >
              {day ? (
                <>
                  <div className="text-sm font-semibold text-foreground">
                    {day.getDate()}
                  </div>
                  {count > 0 && (
                    <div className="space-y-1">
                      {dayBookings.slice(0, 2).map((booking) => (
                        <Button
                          key={booking.id}
                          variant="outline"
                          size="sm"
                          onClick={() => onBookingClick?.(booking.id)}
                          className="text-xs w-full truncate"
                        >
                          {formatTime(new Date(booking.startTime))}
                        </Button>
                      ))}
                      {count > 2 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onBookingClick?.(dayBookings[0].id)}
                          className="text-xs w-full"
                        >
                          +{count - 2} more
                        </Button>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div className="text-muted-foreground text-xs">-</div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
