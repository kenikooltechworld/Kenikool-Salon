import { useState } from "react";
import type { Service, Stylist, PublicSalon } from "@/lib/api/types";
import { useServices } from "@/lib/api/hooks/useServices";
import { useCreateBooking, useAvailability } from "@/lib/api/hooks/useBookings";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Card, CardContent } from "@/components/ui/card";
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  CheckIcon,
  SparklesIcon,
} from "@/components/icons";
// Image removed;
import { WaitlistForm } from "./waitlist-form";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { PromotionsCarousel } from "./promotions-carousel";
import { ServicePackagesSelector } from "./service-packages-selector";
import { SearchAndFilter } from "./search-and-filter";
import { NotificationPreferencesModal } from "./notification-preferences-modal";
import { ConflictDetector } from "./conflict-detector";

interface BookingFlowProps {
  isOpen: boolean;
  onClose: () => void;
  salon: PublicSalon;
  preSelectedService?: Service;
}

type BookingStep = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export function BookingFlow({
  isOpen,
  onClose,
  salon,
  preSelectedService,
}: BookingFlowProps) {
  const [step, setStep] = useState<BookingStep>(preSelectedService ? 2 : 1);
  const [selectedService, setSelectedService] = useState<Service | null>(
    preSelectedService || null,
  );
  const [selectedStylist, setSelectedStylist] = useState<Stylist | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [clientName, setClientName] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [clientWhatsapp, setClientWhatsapp] = useState("");
  const [clientEmail, setClientEmail] = useState("");
  const [bookingNotes, setBookingNotes] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<
    "bank_transfer" | "pay_at_salon" | null
  >(null);
  const [createdBookingId, setCreatedBookingId] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showWaitlist, setShowWaitlist] = useState(false);
  const [showNotificationPrefs, setShowNotificationPrefs] = useState(false);
  const [appliedDiscount, setAppliedDiscount] = useState(0);
  const [selectedPackageId, setSelectedPackageId] = useState<string | null>(
    null,
  );
  const [hasConflict, setHasConflict] = useState(false);

  // Fetch services if not pre-selected
  const { data: services, isLoading: servicesLoading } = useServices({
    is_active: true,
  });

  // Fetch stylists
  const { data: stylists } = useStylists({});

  // Fetch available time slots
  const { data: availabilityData, isLoading: slotsLoading } = useAvailability({
    stylist_id: selectedStylist?.id || "",
    service_id: selectedService?.id || "",
    date: selectedDate,
  });

  const { mutate: createBooking, isPending: bookingLoading } = useCreateBooking(
    {
      onSuccess: (data) => {
        setCreatedBookingId(data.id);
        setStep(7); // Move to payment selection step
      },
      onError: (error) => {
        console.error("Booking error:", error);
        const errorMessage =
          error.response?.data?.message ||
          error.message ||
          "Failed to create booking. Please try again.";
        alert(errorMessage);
      },
    },
  );

  const resetForm = () => {
    setStep(preSelectedService ? 2 : 1);
    if (!preSelectedService) {
      setSelectedService(null);
    }
    setSelectedStylist(null);
    setSelectedDate("");
    setSelectedTime("");
    setClientName("");
    setClientPhone("");
    setClientWhatsapp("");
    setClientEmail("");
    setBookingNotes("");
    setPaymentMethod(null);
    setCreatedBookingId(null);
    setShowSuccess(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async () => {
    if (
      !selectedService ||
      !selectedStylist ||
      !selectedDate ||
      !selectedTime ||
      !clientName ||
      !clientPhone
    ) {
      alert("Please in all required fields");
      return;
    }

    try {
      createBooking({
        service_id: selectedService.id,
        stylist_id: selectedStylist.id,
        booking_date: `${selectedDate}T${selectedTime}`,
        client_name: clientName,
        client_phone: clientPhone,
        client_email: clientEmail || undefined,
        notes: bookingNotes || undefined,
      });
    } catch (error) {
      console.error("Error creating booking:", error);
    }
  };

  const minDate = new Date().toISOString().split("T")[0];

  const canProceedToStep = (targetStep: BookingStep): boolean => {
    switch (targetStep) {
      case 2:
        return !!selectedService;
      case 3:
        return !!selectedService && !!selectedStylist;
      case 4:
        return (
          !!selectedService &&
          !!selectedStylist &&
          !!selectedDate &&
          !!selectedTime &&
          !hasConflict
        );
      case 5:
        return (
          !!selectedService &&
          !!selectedStylist &&
          !!selectedDate &&
          !!selectedTime &&
          !hasConflict
        );
      case 6:
        return (
          !!selectedService &&
          !!selectedStylist &&
          !!selectedDate &&
          !!selectedTime &&
          !!clientName &&
          !!clientPhone &&
          !hasConflict
        );
      case 7:
        return (
          !!selectedService &&
          !!selectedStylist &&
          !!selectedDate &&
          !!selectedTime &&
          !!clientName &&
          !!clientPhone &&
          !!createdBookingId &&
          !hasConflict
        );
      default:
        return true;
    }
  };

  const handlePaymentMethodSelection = async (
    method: "bank_transfer" | "pay_at_salon",
  ) => {
    if (!createdBookingId) return;

    try {
      // Update booking with payment method
      await fetch(
        `/api/bookings/${createdBookingId}/payment-method?payment_method=${method}`,
        {
          method: "PATCH",
        },
      );

      setPaymentMethod(method);
      setShowSuccess(true);
    } catch (error) {
      console.error("Error updating payment method:", error);
      alert("Failed to update payment method");
    }
  };

  // Success confirmation screen
  if (showSuccess) {
    return (
      <Modal open={isOpen} onClose={handleClose} size="md">
        <div className="text-center py-8 space-y-6">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
              <CheckIcon size={40} className="text-green-600" />
            </div>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Booking Confirmed!
            </h2>
            <p className="text-muted-foreground">
              Your appointment has been successfully booked.
            </p>
          </div>
          <div className="bg-muted p-6 rounded-md space-y-3 text-left">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Service:</span>
              <span className="font-medium">{selectedService?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stylist:</span>
              <span className="font-medium">{selectedStylist?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Date:</span>
              <span className="font-medium">
                {new Date(selectedDate).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Time:</span>
              <span className="font-medium">{selectedTime}</span>
            </div>
            <div className="flex justify-between pt-3 border-t border-border">
              <span className="text-muted-foreground">Total:</span>
              <span className="font-bold text-primary text-lg">
                ₦{selectedService?.price.toLocaleString()}
              </span>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            {paymentMethod === "bank_transfer"
              ? "Please complete your bank transfer using the details provided. Send proof to the salon's WhatsApp."
              : "You can pay when you arrive at the salon."}
          </p>
          <Button fullWidth onClick={handleClose}>
            Done
          </Button>
        </div>
      </Modal>
    );
  }

  return (
    <Modal open={isOpen} onClose={handleClose} size="lg">
      <div className="space-y-6">
        {/* Modal Title */}
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            Book an Appointment
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            {salon.business_name}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4, 5, 6, 7].map((s, idx) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm transition-colors ${
                  step >= s
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {step > s ? <CheckIcon size={16} /> : s}
              </div>
              {idx < 6 && (
                <div
                  className={`flex-1 h-1 mx-1 transition-colors ${
                    step > s ? "bg-primary" : "bg-muted"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Select Service */}
        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <SparklesIcon size={20} />
              Select a Service
            </h3>

            {/* Search and Filter */}
            <SearchAndFilter searchType="services" />

            {servicesLoading ? (
              <div className="flex justify-center py-8">
                <Spinner size="lg" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                {services && services.length > 0 ? (
                  services.map((service) => (
                    <div
                      key={service.id}
                      onClick={() => setSelectedService(service)}
                      className={`p-4 rounded-md border-2 cursor-pointer transition-all ${
                        selectedService?.id === service.id
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary"
                      }`}
                    >
                      {service.photo_url && (
                        <div className="relative w-full h-32 mb-3 rounded-md overflow-hidden">
                          <img
                            src={service.photo_url}
                            alt={service.name}
                            className="object-cover"
                          />
                        </div>
                      )}
                      <h4 className="font-semibold text-foreground">
                        {service.name}
                      </h4>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {service.description}
                      </p>
                      <div className="flex items-center justify-between mt-3">
                        <Badge variant="secondary">{service.category}</Badge>
                        <span className="font-bold text-primary">
                          ₦{service.price.toLocaleString()}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        <ClockIcon size={12} className="inline mr-1" />
                        {service.duration_minutes} mins
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground col-span-full text-center py-8">
                    No services available
                  </p>
                )}
              </div>
            )}
            <div className="flex gap-4 pt-4">
              <Button variant="outline" fullWidth onClick={handleClose}>
                Cancel
              </Button>
              <Button
                fullWidth
                disabled={!canProceedToStep(2)}
                onClick={() => setStep(2)}
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Choose Stylist */}
        {step === 2 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <UserIcon size={20} />
              Choose Your Stylist
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {stylists && stylists.length > 0 ? (
                stylists
                  .filter((stylist) =>
                    selectedService?.assigned_stylists?.includes(stylist.id),
                  )
                  .map((stylist) => (
                    <div
                      key={stylist.id}
                      onClick={() => setSelectedStylist(stylist)}
                      className={`p-4 rounded-md border-2 cursor-pointer transition-all text-center ${
                        selectedStylist?.id === stylist.id
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary"
                      }`}
                    >
                      {stylist.photo_url && (
                        <div className="relative w-20 h-20 mx-auto mb-3 rounded-full overflow-hidden">
                          <img
                            src={stylist.photo_url}
                            alt={stylist.name}
                            className="object-cover"
                          />
                        </div>
                      )}
                      <p className="font-medium text-foreground">
                        {stylist.name}
                      </p>
                      {stylist.bio && (
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {stylist.bio}
                        </p>
                      )}
                    </div>
                  ))
              ) : (
                <p className="text-muted-foreground col-span-full text-center py-8">
                  No stylists available for this service
                </p>
              )}
            </div>
            <div className="flex gap-4 pt-4">
              <Button
                variant="outline"
                fullWidth
                onClick={() => setStep(preSelectedService ? 2 : 1)}
              >
                Back
              </Button>
              <Button
                fullWidth
                disabled={!canProceedToStep(3)}
                onClick={() => setStep(3)}
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Pick Date & Time */}
        {step === 3 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
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
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setSelectedTime(""); // Reset time when date changes
                    setHasConflict(false); // Reset conflict state
                  }}
                  className="mt-2"
                />
              </div>

              {selectedDate && (
                <div>
                  <Label required>Available Time Slots</Label>
                  {slotsLoading ? (
                    <div className="flex justify-center py-4">
                      <Spinner />
                    </div>
                  ) : !availabilityData?.slots ||
                    availabilityData.slots.filter((s) => s.available).length ===
                      0 ? (
                    <div className="mt-2 p-4 bg-muted rounded-md space-y-3">
                      <p className="text-sm text-muted-foreground">
                        No available slots for this date.
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setShowWaitlist(true)}
                      >
                        Join Waitlist
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-3 md:grid-cols-4 gap-2 mt-2 max-h-64 overflow-y-auto">
                      {availabilityData?.slots
                        .filter((slot) => slot.available)
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

              {/* Conflict Detection */}
              {selectedDate &&
                selectedTime &&
                selectedStylist &&
                selectedService && (
                  <ConflictDetector
                    stylistId={selectedStylist.id}
                    serviceId={selectedService.id}
                    startTime={`${selectedDate}T${selectedTime}`}
                    endTime={new Date(
                      new Date(`${selectedDate}T${selectedTime}`).getTime() +
                        (selectedService.duration_minutes || 60) * 60 * 1000,
                    )
                      .toISOString()
                      .slice(0, 19)}
                    onConflictDetected={setHasConflict}
                  />
                )}
            </div>
            <div className="flex gap-4 pt-4">
              <Button variant="outline" fullWidth onClick={() => setStep(2)}>
                Back
              </Button>
              <Button
                fullWidth
                disabled={!canProceedToStep(4)}
                onClick={() => setStep(4)}
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 4: Promotions & Packages */}
        {step === 4 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Special Offers</h3>
            <PromotionsCarousel
              bookingAmount={selectedService?.price || 0}
              onPromoApplied={setAppliedDiscount}
            />
            <ServicePackagesSelector
              onPackageSelect={(pkgId, price) => {
                setSelectedPackageId(pkgId);
              }}
            />
            <div className="flex gap-4 pt-4">
              <Button variant="outline" fullWidth onClick={() => setStep(3)}>
                Back
              </Button>
              <Button fullWidth onClick={() => setStep(5)}>
                Continue
              </Button>
            </div>
          </div>
        )}

        {/* Step 5: Enter Client Details */}
        {step === 5 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Your Details</h3>
            <div className="space-y-4">
              <div>
                <Label required>Full Name</Label>
                <Input
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Enter your full name"
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
                <Label>WhatsApp Number</Label>
                <Input
                  type="tel"
                  value={clientWhatsapp}
                  onChange={(e) => setClientWhatsapp(e.target.value)}
                  placeholder="080XXXXXXXX (optional)"
                  className="mt-2"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Leave blank to use phone number
                </p>
              </div>
              <div>
                <Label>Email Address</Label>
                <Input
                  type="email"
                  value={clientEmail}
                  onChange={(e) => setClientEmail(e.target.value)}
                  placeholder="your@email.com (optional)"
                  className="mt-2"
                />
              </div>
              <div>
                <Label>Special Requests</Label>
                <Input
                  value={bookingNotes}
                  onChange={(e) => setBookingNotes(e.target.value)}
                  placeholder="Any special requests? (optional)"
                  className="mt-2"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowNotificationPrefs(true)}
              >
                Set Notification Preferences
              </Button>
            </div>
            <div className="flex gap-4 pt-4">
              <Button variant="outline" fullWidth onClick={() => setStep(4)}>
                Back
              </Button>
              <Button
                fullWidth
                disabled={!canProceedToStep(6)}
                onClick={() => setStep(6)}
              >
                Review Booking
              </Button>
            </div>
          </div>
        )}

        {/* Step 6: Confirm Booking */}
        {step === 6 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Confirm Your Booking</h3>
            <Card>
              <CardContent className="pt-6 space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Service</p>
                  <p className="font-semibold text-foreground">
                    {selectedService?.name}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {selectedService?.duration_minutes} minutes
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Stylist</p>
                  <p className="font-semibold text-foreground">
                    {selectedStylist?.name}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Date & Time
                  </p>
                  <p className="font-semibold text-foreground">
                    {new Date(selectedDate).toLocaleDateString("en-US", {
                      weekday: "long",
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                  <p className="text-sm text-foreground">{selectedTime}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Contact Details
                  </p>
                  <p className="font-semibold text-foreground">{clientName}</p>
                  <p className="text-sm text-foreground">{clientPhone}</p>
                  {clientEmail && (
                    <p className="text-sm text-foreground">{clientEmail}</p>
                  )}
                </div>
                {bookingNotes && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">
                      Special Requests
                    </p>
                    <p className="text-sm text-foreground">{bookingNotes}</p>
                  </div>
                )}
                <div className="pt-4 border-t border-border">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Total Price</span>
                    <span className="text-2xl font-bold text-primary">
                      ₦
                      {(
                        (selectedService?.price || 0) - appliedDiscount
                      ).toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-900">
                <strong>Note:</strong> You will receive a confirmation via
                WhatsApp/SMS. Please arrive 5 minutes before your appointment
                time.
              </p>
            </div>
            <div className="flex gap-4 pt-4">
              <Button variant="outline" fullWidth onClick={() => setStep(5)}>
                Back
              </Button>
              <Button fullWidth loading={bookingLoading} onClick={handleSubmit}>
                Continue to Payment
              </Button>
            </div>
          </div>
        )}

        {/* Step 7: Choose Payment Method */}
        {step === 7 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Choose Payment Method</h3>
            <p className="text-sm text-muted-foreground">
              How would you like to pay for your appointment?
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Pay Online (Bank Transfer) */}
              <div
                onClick={() => handlePaymentMethodSelection("bank_transfer")}
                className="p-6 rounded-lg border-2 border-border hover:border-primary cursor-pointer transition-all space-y-3"
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-foreground">Pay Online</h4>
                  <Badge variant="primary">Recommended</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Transfer to our bank account and upload proof of payment
                </p>
                <div className="pt-3 space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckIcon size={16} />
                    <span>Secure your slot immediately</span>
                  </div>
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckIcon size={16} />
                    <span>No need to carry cash</span>
                  </div>
                </div>
              </div>

              {/* Pay at Salon */}
              <div
                onClick={() => handlePaymentMethodSelection("pay_at_salon")}
                className="p-6 rounded-lg border-2 border-border hover:border-primary cursor-pointer transition-all space-y-3"
              >
                <h4 className="font-semibold text-foreground">Pay at Salon</h4>
                <p className="text-sm text-muted-foreground">
                  Pay when you arrive for your appointment
                </p>
                <div className="pt-3 space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-blue-600">
                    <CheckIcon size={16} />
                    <span>Pay with cash or card</span>
                  </div>
                  <div className="flex items-center gap-2 text-blue-600">
                    <CheckIcon size={16} />
                    <span>Flexible payment options</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bank Details (shown for reference) */}
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm font-semibold text-blue-900 mb-2">
                Bank Transfer Details:
              </p>
              <div className="space-y-1 text-sm text-blue-800">
                <p>
                  <strong>Bank:</strong>{" "}
                  {salon.bank_name || "Contact salon for details"}
                </p>
                <p>
                  <strong>Account Name:</strong>{" "}
                  {salon.account_name || salon.business_name}
                </p>
                <p>
                  <strong>Account Number:</strong>{" "}
                  {salon.account_number || "Contact salon"}
                </p>
                <p className="text-xs text-blue-600 mt-2">
                  After transfer, please send proof to {salon.phone} via
                  WhatsApp
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <WaitlistForm
        isOpen={showWaitlist}
        onClose={() => setShowWaitlist(false)}
        salon={salon}
        service={selectedService || undefined}
      />

      <NotificationPreferencesModal
        isOpen={showNotificationPrefs}
        onClose={() => setShowNotificationPrefs(false)}
        email={clientEmail}
      />
    </Modal>
  );
}
