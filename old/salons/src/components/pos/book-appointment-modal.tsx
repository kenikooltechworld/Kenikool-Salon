import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { useServices } from "@/lib/api/hooks/useServices";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useCreateBooking } from "@/lib/api/hooks/useBookings";
import { CalendarIcon, ClockIcon } from "@/components/icons";

interface BookAppointmentModalProps {
  open: boolean;
  onClose: () => void;
  clientId?: string;
  clientName?: string;
  clientPhone?: string;
  stylistId?: string;
  lastServiceId?: string;
}

export function BookAppointmentModal({
  open,
  onClose,
  clientId,
  clientName,
  clientPhone,
  stylistId,
  lastServiceId,
}: BookAppointmentModalProps) {
  const [selectedServiceId, setSelectedServiceId] = useState(
    lastServiceId || ""
  );
  const [selectedStylistId, setSelectedStylistId] = useState(stylistId || "");
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [selectedTime, setSelectedTime] = useState("");
  const [notes, setNotes] = useState("");

  const { data: servicesData } = useServices();
  const services = Array.isArray(servicesData) ? servicesData : [];
  const { data: stylistsData } = useStylists();
  const stylists = Array.isArray(stylistsData) ? stylistsData : [];
  const createBooking = useCreateBooking();

  // Generate time slots (9 AM to 6 PM, 30-minute intervals)
  const timeSlots = [];
  for (let hour = 9; hour <= 18; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      if (hour === 18 && minute > 0) break;
      const time = `${hour.toString().padStart(2, "0")}:${minute
        .toString()
        .padStart(2, "0")}`;
      timeSlots.push(time);
    }
  }

  const handleBookAppointment = async () => {
    if (!clientName || !clientPhone) {
      toast.error("Client information is required");
      return;
    }

    if (!selectedServiceId) {
      toast.error("Please select a service");
      return;
    }

    if (!selectedStylistId) {
      toast.error("Please select a stylist");
      return;
    }

    if (!selectedDate || !selectedTime) {
      toast.error("Please select date and time");
      return;
    }

    try {
      const bookingDateTime = new Date(selectedDate);
      const [hours, minutes] = selectedTime.split(":");
      bookingDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      await createBooking.mutateAsync({
        client_name: clientName,
        client_phone: clientPhone,
        service_id: selectedServiceId,
        stylist_id: selectedStylistId,
        booking_date: bookingDateTime.toISOString(),
        notes: notes || undefined,
      });

      toast.success("Appointment booked successfully!");
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to book appointment");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Book Next Appointment</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Client Info */}
          <div className="p-4 bg-muted rounded-lg">
            <p className="font-medium">{clientName || "Walk-in Customer"}</p>
            <p className="text-sm text-muted-foreground">
              {clientPhone || "No phone"}
            </p>
          </div>

          {/* Service Selection */}
          <div className="space-y-2">
            <Label>Service</Label>
            <Select
              value={selectedServiceId}
              onValueChange={setSelectedServiceId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select service" />
              </SelectTrigger>
              <SelectContent>
                {services.map((service: any) => (
                  <SelectItem key={service.id} value={service.id}>
                    {service.name} - ${service.price} (
                    {service.duration_minutes || service.duration}min)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {lastServiceId && (
              <p className="text-xs text-muted-foreground">
                💡 Last service pre-selected for quick rebooking
              </p>
            )}
          </div>

          {/* Stylist Selection */}
          <div className="space-y-2">
            <Label>Stylist</Label>
            <Select
              value={selectedStylistId}
              onValueChange={setSelectedStylistId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select stylist" />
              </SelectTrigger>
              <SelectContent>
                {stylists.map((stylist: any) => (
                  <SelectItem key={stylist.id} value={stylist.id}>
                    {stylist.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date Selection */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <CalendarIcon className="h-4 w-4" />
              Date
            </Label>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              disabled={(date) => date < new Date()}
              className="rounded-md border"
            />
          </div>

          {/* Time Selection */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <ClockIcon className="h-4 w-4" />
              Time
            </Label>
            <Select value={selectedTime} onValueChange={setSelectedTime}>
              <SelectTrigger>
                <SelectValue placeholder="Select time" />
              </SelectTrigger>
              <SelectContent className="max-h-60">
                {timeSlots.map((time) => (
                  <SelectItem key={time} value={time}>
                    {time}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label>Notes (Optional)</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any special requests or notes..."
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleBookAppointment}
              disabled={createBooking.isPending}
              className="flex-1"
            >
              {createBooking.isPending ? "Booking..." : "Confirm Appointment"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
