import { useState } from "react";
import { Service, Salon, Stylist, TimeSlot } from "@/lib/types/salon";
import { useAvailability, useCreateBooking } from "@/lib/api/hooks/useBookings";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  CheckIcon,
} from "@/components/icons";

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: Service;
  salon: Salon;
}

export function BookingModal({
  isOpen,
  onClose,
  service,
  salon,
}: BookingModalProps) {
  const [step, setStep] = useState(1);
  const [selectedStylist, setSelectedStylist] = useState<Stylist | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [clientName, setClientName] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [clientWhatsapp, setClientWhatsapp] = useState("");
  const { showToast } = useToast();

  const { data: slotsData, isLoading: slotsLoading } = useAvailability(
    {
      stylist_id: selectedStylist?.id || "",
      service_id: service.id,
      date: selectedDate,
    },
    {
      enabled: !!selectedStylist && !!selectedDate,
    }
  );

  const createBookingMutation = useCreateBooking({
    onSuccess: () => {
      showToast({
        title: "Booking Confirmed!",
        description: "You will receive a confirmation via WhatsApp/SMS",
        variant: "success",
      });
      onClose();
      resetForm();
    },
    onError: (error) => {
      showToast({
        title: "Booking Failed",
        description: error.message,
        variant: "error",
      });
    },
  });

  const resetForm = () => {
    setStep(1);
    setSelectedStylist(null);
    setSelectedDate("");
    setSelectedTime("");
    setClientName("");
    setClientPhone("");
    setClientWhatsapp("");
  };

  const handleSubmit = () => {
    if (
      !selectedStylist ||
      !selectedDate ||
      !selectedTime ||
      !clientName ||
      !clientPhone
    ) {
      showToast({
        title: "Missing Information",
        description: "Please in all required fields",
        variant: "warning",
      });
      return;
    }

    createBookingMutation.mutate({
      client_name: clientName,
      client_phone: clientPhone,
      client_email: undefined,
      service_id: service.id,
      stylist_id: selectedStylist.id,
      booking_date: `${selectedDate}T${selectedTime}:00`,
      notes: undefined,
    });
  };

  const minDate = new Date().toISOString().split("T")[0];

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        {/* Modal Title */}
        <h2 className="text-2xl font-bold text-[var(--foreground)]">
          Book {service.name}
        </h2>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  step >= s
                    ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                    : "bg-[var(--muted)] text-[var(--muted-foreground)]"
                }`}
              >
                {step > s ? <CheckIcon size={16} /> : s}
              </div>
              {s < 3 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    step > s ? "bg-[var(--primary)]" : "bg-[var(--muted)]"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Select Stylist */}
        {step === 1 && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <UserIcon size={20} />
              Select Your Stylist
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {service.stylists.map((stylist) => (
                <div
                  key={stylist.id}
                  onClick={() => setSelectedStylist(stylist)}
                  className={`p-4 rounded-[var(--radius-md)] border-2 cursor-pointer transition-all ${
                    selectedStylist?.id === stylist.id
                      ? "border-[var(--primary)] bg-[var(--primary)]/10"
                      : "border-[var(--border)] hover:border-[var(--primary)]"
                  }`}
                >
                  {stylist.photo && (
                    <img
                      src={stylist.photo}
                      alt={stylist.name}
                      className="w-16 h-16 rounded-full mx-auto mb-2 object-cover"
                    />
                  )}
                  <p className="text-center font-medium">{stylist.name}</p>
                </div>
              ))}
            </div>
            <Button
              fullWidth
              className="mt-6"
              disabled={!selectedStylist}
              onClick={() => setStep(2)}
            >
              Continue
            </Button>
          </div>
        )}

        {/* Step 2: Select Date & Time */}
        {step === 2 && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <CalendarIcon size={20} />
              Select Date & Time
            </h3>
            <div className="space-y-4">
              <div>
                <Label required>Date</Label>
                <Input
                  type="date"
                  min={minDate}
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="mt-2"
                />
              </div>

              {selectedDate && (
                <div>
                  <Label required>Available Time Slots</Label>
                  {slotsLoading ? (
                    <p className="text-sm text-[var(--muted-foreground)] mt-2">
                      Loading slots...
                    </p>
                  ) : (
                    <div className="grid grid-cols-4 gap-2 mt-2">
                      {slotsData?.slots
                        ?.filter((slot) => slot.available)
                        .map((slot) => (
                          <Button
                            key={slot.start_time}
                            size="sm"
                            variant={
                              selectedTime === slot.start_time
                                ? "primary"
                                : "outline"
                            }
                            onClick={() => setSelectedTime(slot.start_time)}
                          >
                            {slot.start_time}
                          </Button>
                        ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="flex gap-4 mt-6">
              <Button variant="outline" fullWidth onClick={() => setStep(1)}>
                Back
              </Button>
              <Button
                fullWidth
                disabled={!selectedDate || !selectedTime}
                onClick={() => setStep(3)}
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Client Details */}
        {step === 3 && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Your Details</h3>
            <div className="space-y-4">
              <div>
                <Label required>Full Name</Label>
                <Input
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Enter your name"
                  className="mt-2"
                />
              </div>
              <div>
                <Label required>Phone Number</Label>
                <Input
                  type="tel"
                  value={clientPhone}
                  onChange={(e) => setClientPhone(e.target.value)}
                  placeholder="080XXXXXXXX"
                  className="mt-2"
                />
              </div>
              <div>
                <Label>WhatsApp Number (Optional)</Label>
                <Input
                  type="tel"
                  value={clientWhatsapp}
                  onChange={(e) => setClientWhatsapp(e.target.value)}
                  placeholder="080XXXXXXXX"
                  className="mt-2"
                />
              </div>

              {/* Booking Summary */}
              <div className="bg-[var(--muted)] p-4 rounded-[var(--radius-md)] mt-6">
                <h4 className="font-semibold mb-3">Booking Summary</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">
                      Service:
                    </span>
                    <span className="font-medium">{service.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">
                      Stylist:
                    </span>
                    <span className="font-medium">{selectedStylist?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">
                      Date:
                    </span>
                    <span className="font-medium">
                      {new Date(selectedDate).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">
                      Time:
                    </span>
                    <span className="font-medium">{selectedTime}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-[var(--border)]">
                    <span className="text-[var(--muted-foreground)]">
                      Price:
                    </span>
                    <span className="font-bold text-[var(--primary)]">
                      ₦{service.price.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex gap-4 mt-6">
              <Button variant="outline" fullWidth onClick={() => setStep(2)}>
                Back
              </Button>
              <Button
                fullWidth
                loading={createBookingMutation.isPending}
                onClick={handleSubmit}
              >
                Confirm Booking
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
