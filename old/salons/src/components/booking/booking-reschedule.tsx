import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";

interface BookingRescheduleProps {
  isOpen: boolean;
  onClose: () => void;
  bookingId: string;
  currentDate: string;
  currentTime: string;
  stylistId: string;
  serviceId: string;
}

export function BookingReschedule({
  isOpen,
  onClose,
  bookingId,
  currentDate,
  currentTime,
  stylistId,
  serviceId,
}: BookingRescheduleProps) {
  const { toast } = useToast();
  const [newDate, setNewDate] = useState("");
  const [newTime, setNewTime] = useState("");
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const minDate = new Date().toISOString().split("T")[0];

  const rescheduleMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.patch(
        `/api/bookings/${bookingId}/reschedule`,
        {
          new_date: newDate,
          new_time: newTime,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      toast("Booking rescheduled successfully", "success");
      onClose();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to reschedule booking",
        "error"
      );
    },
  });

  const handleDateChange = async (date: string) => {
    setNewDate(date);
    setNewTime("");
    setLoadingSlots(true);

    try {
      const response = await apiClient.get("/api/availability", {
        params: {
          stylist_id: stylistId,
          service_id: serviceId,
          date: date,
        },
      });

      const slots = response.data.slots
        ?.filter((s: any) => s.available)
        .map((s: any) => s.start_time) || [];
      setAvailableSlots(slots);
    } catch (error) {
      toast("Failed to load available slots", "error");
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleSubmit = async () => {
    if (!newDate || !newTime) {
      toast("Please select a new date and time", "error");
      return;
    }

    await rescheduleMutation.mutateAsync();
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Reschedule Booking</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {/* Current Booking Info */}
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-[var(--muted-foreground)] mb-1">
              Current Appointment
            </p>
            <p className="font-semibold text-[var(--foreground)]">
              {new Date(currentDate).toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
            <p className="text-sm text-[var(--foreground)]">{currentTime}</p>
          </CardContent>
        </Card>

        {/* New Date Selection */}
        <div>
          <Label required>New Date</Label>
          <Input
            type="date"
            min={minDate}
            value={newDate}
            onChange={(e) => handleDateChange(e.target.value)}
            className="mt-2"
          />
        </div>

        {/* New Time Selection */}
        {newDate && (
          <div>
            <Label required>Available Time Slots</Label>
            {loadingSlots ? (
              <p className="text-sm text-[var(--muted-foreground)] mt-2">
                Loading available slots...
              </p>
            ) : availableSlots.length > 0 ? (
              <div className="grid grid-cols-3 gap-2 mt-2 max-h-48 overflow-y-auto">
                {availableSlots.map((slot) => (
                  <Button
                    key={slot}
                    size="sm"
                    variant={newTime === slot ? "primary" : "outline"}
                    onClick={() => setNewTime(slot)}
                  >
                    {slot}
                  </Button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--muted-foreground)] mt-2">
                No available slots for this date
              </p>
            )}
          </div>
        )}
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={rescheduleMutation.isPending || !newDate || !newTime}
        >
          {rescheduleMutation.isPending ? "Rescheduling..." : "Confirm Reschedule"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
