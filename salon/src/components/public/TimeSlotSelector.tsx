/**
 * Time Slot Selector Component - Display available time slots for public booking
 */

import { useState } from "react";
import { Card, Button, Spinner } from "@/components/ui";
import { usePublicAvailability } from "@/hooks/usePublicBooking";
import { addDays } from "@/lib/utils/date";
import { formatDate } from "@/lib/utils/format";

interface TimeSlotSelectorProps {
  serviceId: string;
  staffId: string;
  onSelect: (bookingDate: string, bookingTime: string) => void;
}

export default function TimeSlotSelector({
  serviceId,
  staffId,
  onSelect,
}: TimeSlotSelectorProps) {
  const [selectedDate, setSelectedDate] = useState<Date>(
    addDays(new Date(), 1),
  );
  const [selectedTime, setSelectedTime] = useState<string | null>(null);

  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const dateStr = getLocalDateString(selectedDate);
  const {
    data: availability,
    isLoading,
    error,
  } = usePublicAvailability(serviceId, staffId, dateStr);

  const handleDateChange = (date: Date) => {
    setSelectedDate(date);
    setSelectedTime(null);
  };

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time);
    onSelect(dateStr, time);
  };

  const availableDates = Array.from({ length: 30 }, (_, i) =>
    addDays(new Date(), i + 1),
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Select Date & Time</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Choose your preferred appointment time
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Date Picker */}
        <div>
          <h3 className="font-semibold mb-3">Select Date</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {availableDates.map((date) => (
              <Button
                key={date.toISOString()}
                variant={
                  selectedDate.toDateString() === date.toDateString()
                    ? "primary"
                    : "outline"
                }
                className="w-full justify-start text-left"
                onClick={() => handleDateChange(date)}
              >
                {formatDate(date, "MMM dd, yyyy")}
              </Button>
            ))}
          </div>
        </div>

        {/* Time Slots */}
        <div className="md:col-span-2">
          <h3 className="font-semibold mb-3">
            Available Times for {formatDate(selectedDate, "MMM dd")}
          </h3>

          {isLoading && (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          )}

          {error && (
            <div className="text-center py-8">
              <p className="text-destructive">
                Failed to load availability. Please try again.
              </p>
            </div>
          )}

          {availability && availability.slots.length === 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                No available slots for this date. Please select another date.
              </p>
            </div>
          )}

          {availability && availability.slots.length > 0 && (
            <div className="grid grid-cols-3 gap-2">
              {availability.slots.map((slot) => (
                <Button
                  key={slot.time}
                  variant={
                    selectedTime === slot.time
                      ? "primary"
                      : slot.available
                        ? "outline"
                        : "ghost"
                  }
                  disabled={!slot.available}
                  className="text-sm"
                  onClick={() => handleTimeSelect(slot.time)}
                >
                  {slot.time}
                </Button>
              ))}
            </div>
          )}

          {selectedTime && (
            <Card className="mt-6 p-4 bg-primary/5">
              <p className="text-sm text-muted-foreground">
                Selected:{" "}
                <strong>{formatDate(selectedDate, "MMM dd, yyyy")}</strong> at{" "}
                <strong>{selectedTime}</strong>
              </p>
            </Card>
          )}
        </div>
      </div>

      {selectedTime && (
        <div className="flex justify-end">
          <Button variant="primary">Continue →</Button>
        </div>
      )}
    </div>
  );
}
