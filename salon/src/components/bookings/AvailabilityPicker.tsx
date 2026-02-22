import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAvailableSlots } from "@/hooks/useAvailability";
import type { AvailableSlot } from "@/types";
import { formatTime } from "@/lib/utils/format";
import { CheckIcon, CalendarIcon } from "@/components/icons";

interface AvailabilityPickerProps {
  staffId: string;
  serviceId: string;
  serviceDuration: number;
  selectedSlot?: AvailableSlot;
  onSlotSelect: (slot: AvailableSlot) => void;
  onDateSelect?: (date: string) => void;
  onNext?: () => void;
  minDate?: Date;
  maxDate?: Date;
}

export function AvailabilityPicker({
  staffId,
  serviceId,
  serviceDuration,
  selectedSlot,
  onSlotSelect,
  onDateSelect,
  onNext,
  minDate,
  maxDate,
}: AvailabilityPickerProps) {
  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const [selectedDate, setSelectedDate] = useState<string>(
    getLocalDateString(new Date()),
  );

  const { data: slots = [], isLoading } = useAvailableSlots(
    staffId,
    serviceId,
    selectedDate,
  );

  // Don't filter - show all slots, just disable the booked ones
  const allSlots = slots;

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setSelectedDate(newDate);
    onDateSelect?.(newDate);
  };

  const getMinDateString = () => {
    const date = minDate || new Date();
    // Ensure min date is today or later
    const today = new Date();
    if (date < today) {
      return getLocalDateString(today);
    }
    return getLocalDateString(date);
  };

  const getMaxDateString = () => {
    if (maxDate) {
      return getLocalDateString(maxDate);
    }
    const date = new Date();
    date.setDate(date.getDate() + 30);
    return getLocalDateString(date);
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-2">
          Select Date & Time
        </h3>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Choose an available time slot for your {serviceDuration}-minute
          appointment
        </p>
      </div>

      {/* Date Picker */}
      <div className="space-y-2">
        <label className="text-xs sm:text-sm font-medium text-foreground flex items-center gap-2">
          <CalendarIcon size={16} />
          Select Date
        </label>
        <Input
          type="date"
          value={selectedDate}
          onChange={handleDateChange}
          min={getMinDateString()}
          max={getMaxDateString()}
          className="w-full h-10"
        />
      </div>

      {/* Available Slots */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-foreground">
          Available Times
        </label>
        {isLoading ? (
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-10 sm:h-9 rounded-md" />
            ))}
          </div>
        ) : allSlots.length > 0 ? (
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {allSlots.map((slot: AvailableSlot, index: number) => (
              <Button
                key={index}
                variant={
                  selectedSlot?.start_time === slot.start_time
                    ? "primary"
                    : "outline"
                }
                onClick={() => onSlotSelect(slot)}
                disabled={!slot.isAvailable}
                className="text-xs sm:text-sm h-10 sm:h-9"
              >
                <div className="flex items-center gap-1">
                  {selectedSlot?.start_time === slot.start_time && (
                    <CheckIcon size={14} />
                  )}
                  {formatTime(new Date(`${selectedDate}T${slot.start_time}`))}
                </div>
              </Button>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No available slots for this date
          </div>
        )}
      </div>

      {/* Selected Slot Summary */}
      {selectedSlot && (
        <Card className="p-3 sm:p-4 bg-muted/50 border-primary/50">
          <div className="space-y-2">
            <p className="text-xs sm:text-sm text-muted-foreground">
              Selected Time Slot
            </p>
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <p className="font-semibold text-sm sm:text-base text-foreground">
                  {new Date(selectedDate).toLocaleDateString()}
                </p>
                <p className="text-xs sm:text-sm text-foreground">
                  {formatTime(
                    new Date(`${selectedDate}T${selectedSlot.start_time}`),
                  )}{" "}
                  -{" "}
                  {formatTime(
                    new Date(`${selectedDate}T${selectedSlot.end_time}`),
                  )}
                </p>
              </div>
              <CheckIcon size={20} className="text-primary flex-shrink-0" />
            </div>
          </div>
        </Card>
      )}

      {/* Next Button */}
      {onNext && (
        <Button
          onClick={onNext}
          disabled={!selectedSlot}
          className="w-full h-10"
        >
          Continue to Confirmation
        </Button>
      )}
    </div>
  );
}
