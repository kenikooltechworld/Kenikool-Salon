import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AvailableSlot } from "@/types";
import { formatTime } from "@/lib/utils/format";
import {
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@/components/icons";

interface TimeSlotPickerProps {
  slots: AvailableSlot[];
  selectedSlot?: AvailableSlot;
  onSlotSelect: (slot: AvailableSlot) => void;
  isLoading?: boolean;
  slotsPerRow?: number;
}

export function TimeSlotPicker({
  slots,
  selectedSlot,
  onSlotSelect,
  isLoading = false,
  slotsPerRow = 4,
}: TimeSlotPickerProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const slotsPerPage = slotsPerRow * 3;
  const totalPages = Math.ceil(slots.length / slotsPerPage);
  const startIdx = currentPage * slotsPerPage;
  const endIdx = startIdx + slotsPerPage;
  const currentSlots = slots.slice(startIdx, endIdx);

  const handlePrevious = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const handleNext = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };

  if (isLoading) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Loading available time slots...
      </div>
    );
  }

  if (slots.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No available time slots for this date
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Time Slots Grid */}
      <div className={`grid grid-cols-${slotsPerRow} gap-2`}>
        {currentSlots.map((slot, index) => (
          <Button
            key={index}
            variant={
              selectedSlot?.start_time === slot.start_time
                ? "primary"
                : "outline"
            }
            onClick={() => onSlotSelect(slot)}
            className="text-sm h-auto py-2"
          >
            <div className="flex flex-col items-center gap-1">
              {selectedSlot?.start_time === slot.start_time && (
                <CheckIcon size={14} />
              )}
              <span>
                {formatTime(new Date(`2024-01-01T${slot.start_time}`))}
              </span>
            </div>
          </Button>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevious}
            disabled={currentPage === 0}
          >
            <ChevronLeftIcon size={16} />
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {currentPage + 1} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNext}
            disabled={currentPage === totalPages - 1}
          >
            <ChevronRightIcon size={16} />
          </Button>
        </div>
      )}

      {/* Selected Slot Summary */}
      {selectedSlot && (
        <Card className="p-3 bg-muted/50 border-primary/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">Selected Time</p>
              <p className="font-semibold text-foreground">
                {formatTime(new Date(`2024-01-01T${selectedSlot.start_time}`))}{" "}
                - {formatTime(new Date(`2024-01-01T${selectedSlot.end_time}`))}
              </p>
            </div>
            <CheckIcon size={18} className="text-primary" />
          </div>
        </Card>
      )}
    </div>
  );
}
