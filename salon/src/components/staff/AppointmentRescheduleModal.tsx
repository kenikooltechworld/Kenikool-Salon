import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAvailableSlots } from "@/hooks/useAvailability";
import { formatDate, formatTime } from "@/lib/utils/format";

interface AppointmentRescheduleModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (newStartTime: string, newEndTime: string) => void;
  appointmentId: string;
  staffId: string;
  serviceId: string;
  currentStartTime: string;
  isLoading?: boolean;
}

export default function AppointmentRescheduleModal({
  open,
  onOpenChange,
  onConfirm,
  appointmentId,
  staffId,
  serviceId,
  currentStartTime,
  isLoading = false,
}: AppointmentRescheduleModalProps) {
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState<{
    startTime: string;
    endTime: string;
  } | null>(null);

  // Initialize with current date or tomorrow
  useEffect(() => {
    if (open && !selectedDate) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      setSelectedDate(tomorrow.toISOString().split("T")[0]);
    }
  }, [open, selectedDate]);

  const {
    data: availableSlots,
    isLoading: slotsLoading,
    error: slotsError,
  } = useAvailableSlots(staffId, serviceId, selectedDate, {
    enabled: open && !!selectedDate,
  });

  const handleConfirm = () => {
    if (selectedSlot) {
      onConfirm(selectedSlot.startTime, selectedSlot.endTime);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      setSelectedDate("");
      setSelectedSlot(null);
      onOpenChange(false);
    }
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
    setSelectedSlot(null);
  };

  const handleSlotSelect = (startTime: string, endTime: string) => {
    setSelectedSlot({ startTime, endTime });
  };

  // Get minimum date (tomorrow)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split("T")[0];

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Reschedule Appointment</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="rounded-lg bg-muted/50 p-3">
            <p className="text-sm text-muted-foreground">
              Current appointment: {formatDate(new Date(currentStartTime))} at{" "}
              {formatTime(new Date(currentStartTime))}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="reschedule-date">Select New Date</Label>
            <Input
              id="reschedule-date"
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              min={minDate}
              disabled={isLoading}
            />
          </div>

          {selectedDate && (
            <div className="space-y-2">
              <Label>Available Time Slots</Label>
              <div className="border border-border rounded-lg p-4 max-h-64 overflow-y-auto">
                {slotsLoading && (
                  <div className="space-y-2">
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                )}

                {slotsError && (
                  <div className="text-sm text-destructive">
                    Failed to load available slots. Please try again.
                  </div>
                )}

                {!slotsLoading &&
                  !slotsError &&
                  availableSlots?.length === 0 && (
                    <div className="text-sm text-muted-foreground text-center py-4">
                      No available slots for this date. Please select another
                      date.
                    </div>
                  )}

                {!slotsLoading &&
                  !slotsError &&
                  availableSlots &&
                  availableSlots.length > 0 && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {availableSlots.map((slot, index) => {
                        const slotStart = new Date(slot.startTime);
                        const slotEnd = new Date(slot.endTime);
                        const isSelected =
                          selectedSlot?.startTime === slot.startTime;

                        return (
                          <Button
                            key={index}
                            variant={isSelected ? "default" : "outline"}
                            size="sm"
                            onClick={() =>
                              handleSlotSelect(slot.startTime, slot.endTime)
                            }
                            disabled={isLoading}
                            className="justify-start"
                          >
                            {formatTime(slotStart)} - {formatTime(slotEnd)}
                          </Button>
                        );
                      })}
                    </div>
                  )}
              </div>
            </div>
          )}

          <div className="rounded-lg bg-muted/50 p-3">
            <p className="text-sm text-muted-foreground">
              The customer will be notified about the rescheduled appointment.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={!selectedSlot || isLoading}>
            {isLoading ? "Rescheduling..." : "Confirm Reschedule"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
