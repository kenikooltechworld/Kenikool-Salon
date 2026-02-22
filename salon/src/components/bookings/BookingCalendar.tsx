import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useBookingsStore } from "@/stores/bookings";
import { useCalendarView } from "@/hooks/useBookings";
import { DayView } from "./DayView";
import { WeekView } from "./WeekView";
import { MonthView } from "./MonthView";

interface BookingCalendarProps {
  onBookingClick?: (bookingId: string) => void;
}

export function BookingCalendar({ onBookingClick }: BookingCalendarProps) {
  const { calendarView, setCalendarView } = useBookingsStore();
  const [currentDate, setCurrentDate] = useState(new Date());

  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const { data: bookings = [], isLoading } = useCalendarView(
    calendarView,
    getLocalDateString(currentDate),
  );

  const handlePrevious = () => {
    const newDate = new Date(currentDate);
    if (calendarView === "day") {
      newDate.setDate(newDate.getDate() - 1);
    } else if (calendarView === "week") {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setMonth(newDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  const handleNext = () => {
    const newDate = new Date(currentDate);
    if (calendarView === "day") {
      newDate.setDate(newDate.getDate() + 1);
    } else if (calendarView === "week") {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  return (
    <div className="space-y-4">
      {/* View Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <div className="flex gap-2">
          <Button
            variant={calendarView === "day" ? "primary" : "outline"}
            onClick={() => setCalendarView("day")}
            size="sm"
            className="text-xs sm:text-sm"
          >
            Day
          </Button>
          <Button
            variant={calendarView === "week" ? "primary" : "outline"}
            onClick={() => setCalendarView("week")}
            size="sm"
            className="text-xs sm:text-sm"
          >
            Week
          </Button>
          <Button
            variant={calendarView === "month" ? "primary" : "outline"}
            onClick={() => setCalendarView("month")}
            size="sm"
            className="text-xs sm:text-sm"
          >
            Month
          </Button>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <Button
            variant="outline"
            onClick={handlePrevious}
            size="sm"
            className="text-xs sm:text-sm"
          >
            ← Prev
          </Button>
          <span className="text-xs sm:text-sm font-medium text-foreground min-w-[120px] sm:min-w-[150px] text-center">
            {currentDate.toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </span>
          <Button
            variant="outline"
            onClick={handleNext}
            size="sm"
            className="text-xs sm:text-sm"
          >
            Next →
          </Button>
        </div>
      </div>

      {/* Calendar Content */}
      <div className="border border-border rounded-lg p-3 sm:p-6 bg-card overflow-x-auto">
        {calendarView === "day" && (
          <DayView
            date={currentDate}
            bookings={bookings}
            onBookingClick={onBookingClick}
            isLoading={isLoading}
          />
        )}
        {calendarView === "week" && (
          <WeekView
            startDate={currentDate}
            bookings={bookings}
            onBookingClick={onBookingClick}
            isLoading={isLoading}
          />
        )}
        {calendarView === "month" && (
          <MonthView
            date={currentDate}
            bookings={bookings}
            onBookingClick={onBookingClick}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
}
