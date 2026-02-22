/**
 * AvailabilityCalendar Component
 * Displays a calendar with available dates highlighted
 * Validates: Requirements 1.2, 14.1
 */
import React, { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { TimeSlot } from "@/lib/api/types";

interface AvailabilityCalendarProps {
  availableSlots: TimeSlot[];
  onDateSelect: (date: string) => void;
  minDate?: Date;
  maxDate?: Date;
  loading?: boolean;
}

/**
 * Calendar component that displays available dates
 * Highlights dates with available time slots
 */
export const AvailabilityCalendar: React.FC<AvailabilityCalendarProps> = ({
  availableSlots,
  onDateSelect,
  minDate = new Date(),
  maxDate,
  loading = false,
}) => {
  const [currentDate, setCurrentDate] = useState(new Date(minDate));

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date: Date) => {
    return date.toISOString().split("T")[0];
  };

  const isDateAvailable = (date: Date) => {
    const dateStr = formatDate(date);
    return availableSlots.some(
      (slot) => slot.timestamp.split("T")[0] === dateStr && slot.available,
    );
  };

  const isDateDisabled = (date: Date) => {
    if (date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  const handlePrevMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1),
    );
  };

  const handleNextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1),
    );
  };

  const handleDateClick = (day: number) => {
    const selectedDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      day,
    );
    if (!isDateDisabled(selectedDate)) {
      onDateSelect(formatDate(selectedDate));
    }
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const days = [];

  // Add empty cells for days before month starts
  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }

  // Add days of month
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day);
  }

  const monthName = currentDate.toLocaleString("default", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <button
          onClick={handlePrevMonth}
          disabled={loading}
          className="rounded p-1 hover:bg-gray-100 disabled:opacity-50"
          aria-label="Previous month"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <h3 className="text-lg font-semibold">{monthName}</h3>
        <button
          onClick={handleNextMonth}
          disabled={loading}
          className="rounded p-1 hover:bg-gray-100 disabled:opacity-50"
          aria-label="Next month"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {/* Day headers */}
      <div className="mb-2 grid grid-cols-7 gap-1">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            className="text-center text-xs font-semibold text-gray-600"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => {
          if (day === null) {
            return <div key={`empty-${index}`} className="aspect-square" />;
          }

          const date = new Date(
            currentDate.getFullYear(),
            currentDate.getMonth(),
            day,
          );
          const isDisabled = isDateDisabled(date);
          const isAvailable = isDateAvailable(date);
          const dateStr = formatDate(date);

          return (
            <button
              key={day}
              onClick={() => handleDateClick(day)}
              disabled={isDisabled || loading}
              className={`aspect-square rounded text-sm font-medium transition-colors ${
                isDisabled
                  ? "cursor-not-allowed bg-gray-50 text-gray-300"
                  : isAvailable
                    ? "cursor-pointer bg-green-100 text-green-900 hover:bg-green-200"
                    : "cursor-not-allowed bg-gray-100 text-gray-500"
              }`}
              title={
                isAvailable
                  ? `Available on ${dateStr}`
                  : isDisabled
                    ? "Date not available"
                    : "No availability"
              }
            >
              {day}
            </button>
          );
        })}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="mt-4 text-center text-sm text-gray-500">
          Loading availability...
        </div>
      )}
    </div>
  );
};

export default AvailabilityCalendar;
