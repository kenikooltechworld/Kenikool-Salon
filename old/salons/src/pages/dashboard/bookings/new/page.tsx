import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import {
  ArrowLeftIcon,
  ServiceIcon,
  CheckIcon,
  UserIcon,
} from "@/components/icons";
import { useServices } from "@/lib/api/hooks/useServices";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useLocations } from "@/lib/api/hooks/useLocations";
import { useAvailability } from "@/lib/api/hooks/useAvailability";
import { useCreateBooking } from "@/lib/api/hooks/useCreateBooking";
import { useServiceVariants } from "@/lib/api/hooks/useServiceVariants";
import { usePackageCreditBalance } from "@/lib/api/hooks/usePackageCredits";
import { useClients } from "@/lib/api/hooks/useClients";
import { VariantSelector } from "@/components/booking/variant-selector";
import { AddOnSelector } from "@/components/booking/add-on-selector";
import { CostCalculator } from "@/components/booking/cost-calculator";
import { PaymentMethodSelector } from "@/components/booking/payment-method-selector";
import { toast } from "sonner";

interface BookingFormData {
  clientId: string;
  clientName: string;
  clientPhone: string;
  clientEmail: string;
  serviceId: string;
  stylistId: string;
  locationId: string;
  bookingDate: string;
  bookingTime: string;
  duration: number;
  price: number;
  notes: string;
  selectedVariantId?: string;
  selectedAddOnIds: string[];
  paymentMethod?: string;
  creditsToApply: number;
}

interface TimeSlot {
  time: string;
  timestamp: string;
  available: boolean;
}

export default function NewBookingPage() {
  const navigate = useNavigate();
  const [clientType, setClientType] = useState<"existing" | "new">("existing");
  const [clientSearch, setClientSearch] = useState("");
  const [selectedDate, setSelectedDate] = useState("");
  const [formData, setFormData] = useState<BookingFormData>({
    clientId: "",
    clientName: "",
    clientPhone: "",
    clientEmail: "",
    serviceId: "",
    stylistId: "",
    locationId: "",
    bookingDate: "",
    bookingTime: "",
    duration: 60,
    price: 0,
    notes: "",
    selectedAddOnIds: [],
    creditsToApply: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);

  // API hooks
  const { data: services, isLoading: servicesLoading } = useServices();
  const {
    data: stylists,
    isLoading: stylistsLoading,
    error: stylistsError,
  } = useStylists({
    is_active: true,
  });
  const { data: locations, isLoading: locationsLoading } = useLocations();
  const { data: clientsData, isLoading: clientsLoading } = useClients({
    search: clientSearch,
    limit: 10,
  });
  const createBookingMutation = useCreateBooking();

  // Debug logging
  console.log("Stylists data:", stylists);
  console.log("Stylists loading:", stylistsLoading);
  console.log("Stylists error:", stylistsError);
  console.log("Services data:", services);
  console.log("Locations data:", locations);

  // Enhanced hooks for variants, add-ons, and credits
  const {
    variants,
    addOns,
    selectedVariant,
    selectedAddOns,
    selectVariant,
    toggleAddOn,
    calculatePriceModifier,
    calculateDurationModifier,
  } = useServiceVariants(formData.serviceId);
  const { data: creditBalance } = usePackageCreditBalance();

  // Payment methods
  const paymentMethods = [
    {
      id: "card",
      type: "credit_card" as const,
      name: "Credit Card",
      is_default: true,
    },
    { id: "cash", type: "debit_card" as const, name: "Cash" },
    {
      id: "credits",
      type: "package_credits" as const,
      name: "Package Credits",
    },
  ];

  // Availability hook
  const { data: availabilityData, isLoading: availabilityLoading } =
    useAvailability(
      {
        stylist_id: formData.stylistId,
        service_id: formData.serviceId,
        date: selectedDate,
      },
      {
        enabled: !!(formData.stylistId && formData.serviceId && selectedDate),
      },
    );

  // Effects
  useEffect(() => {
    if (availabilityData?.available_slots) {
      setAvailableSlots(availabilityData.available_slots);
    } else {
      setAvailableSlots([]);
    }
  }, [availabilityData]);

  useEffect(() => {
    if (selectedVariant) {
      setFormData((prev) => ({ ...prev, selectedVariantId: selectedVariant }));
    }
  }, [selectedVariant]);

  useEffect(() => {
    setFormData((prev) => ({ ...prev, selectedAddOnIds: selectedAddOns }));
  }, [selectedAddOns]);

  // Handle client selection
  const handleClientSelect = (clientId: string) => {
    const selectedClient = clientsData?.items?.find(
      (c: any) => c.id === clientId,
    );
    if (selectedClient) {
      setFormData((prev) => ({
        ...prev,
        clientId: selectedClient.id,
        clientName: selectedClient.name,
        clientPhone: selectedClient.phone,
        clientEmail: selectedClient.email || "",
      }));
    }
  };

  // Handle date selection from calendar
  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    setFormData((prev) => ({
      ...prev,
      bookingDate: date,
      bookingTime: "", // Reset time when date changes
    }));
  };

  // Calculations
  const calculatedCost = useMemo(() => {
    const basePrice = formData.price;
    const variantCost = calculatePriceModifier();
    const total = basePrice + variantCost - formData.creditsToApply;
    return Math.max(0, total);
  }, [formData.price, calculatePriceModifier, formData.creditsToApply]);

  const calculatedDuration = useMemo(() => {
    const baseDuration = formData.duration;
    const durationModifier = calculateDurationModifier();
    return baseDuration + durationModifier;
  }, [formData.duration, calculateDurationModifier]);
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (
        !formData.clientName ||
        !formData.clientPhone ||
        !formData.serviceId ||
        !formData.stylistId ||
        !formData.locationId
      ) {
        throw new Error("Please fill in all required fields");
      }

      if (!selectedDate || !formData.bookingTime) {
        throw new Error("Please select date and time");
      }

      const bookingDateTime = `${selectedDate}T${formData.bookingTime}:00`;

      const bookingData = {
        location_id: formData.locationId,
        client_name: formData.clientName,
        client_phone: formData.clientPhone,
        client_email: formData.clientEmail || undefined,
        service_id: formData.serviceId,
        stylist_id: formData.stylistId,
        booking_date: bookingDateTime,
        notes: formData.notes || undefined,
        variant_id: formData.selectedVariantId || undefined,
        add_on_ids:
          formData.selectedAddOnIds.length > 0
            ? formData.selectedAddOnIds
            : undefined,
        payment_method: formData.paymentMethod || undefined,
        credits_to_apply:
          formData.creditsToApply > 0 ? formData.creditsToApply : undefined,
      };

      await createBookingMutation.mutateAsync(bookingData);
      toast.success("Booking created successfully!");
      navigate("/dashboard/bookings");
    } catch (error: any) {
      console.error("Failed to create booking:", error);
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        "Failed to create booking";
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // For now, let's create a simplified single-page form that includes all the enhancements
  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Button
            onClick={() => navigate("/dashboard/bookings")}
            variant="ghost"
            size="sm"
          >
            <ArrowLeftIcon size={20} />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-foreground">New Booking</h1>
            <p className="text-sm text-muted-foreground">
              Create a booking with variants, add-ons, and payment options
            </p>
          </div>
        </div>
        <form onSubmit={handleFormSubmit} className="space-y-6">
          {/* Client Information */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <UserIcon size={20} />
              Client Information
            </h2>

            {/* Client Type Toggle */}
            <div className="mb-4">
              <Label>Client Type</Label>
              <div className="flex gap-4 mt-2">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="clientType"
                    value="existing"
                    checked={clientType === "existing"}
                    onChange={(e) =>
                      setClientType(e.target.value as "existing" | "new")
                    }
                  />
                  <span>Existing Client</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="clientType"
                    value="new"
                    checked={clientType === "new"}
                    onChange={(e) =>
                      setClientType(e.target.value as "existing" | "new")
                    }
                  />
                  <span>New Client</span>
                </label>
              </div>
            </div>

            {clientType === "existing" ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="clientSearch">Search Client</Label>
                  <Input
                    id="clientSearch"
                    value={clientSearch}
                    onChange={(e) => setClientSearch(e.target.value)}
                    placeholder="Search by name, phone, or email"
                  />
                </div>

                {clientSearch && (
                  <div className="space-y-2">
                    <Label>Select Client</Label>
                    <Select
                      value={formData.clientId}
                      onValueChange={handleClientSelect}
                    >
                      <SelectTrigger>
                        <SelectValue>
                          {formData.clientId
                            ? formData.clientName
                            : "Select a client"}
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {clientsLoading ? (
                          <SelectItem value="loading" disabled>
                            Loading clients...
                          </SelectItem>
                        ) : clientsData?.items &&
                          clientsData.items.length > 0 ? (
                          clientsData.items.map((client: any) => (
                            <SelectItem key={client.id} value={client.id}>
                              {client.name} - {client.phone}
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem value="none" disabled>
                            No clients found
                          </SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Show selected client info */}
                {formData.clientId && (
                  <div className="p-3 bg-gray-50 rounded border">
                    <p className="font-medium">{formData.clientName}</p>
                    <p className="text-sm text-gray-600">
                      {formData.clientPhone}
                    </p>
                    {formData.clientEmail && (
                      <p className="text-sm text-gray-600">
                        {formData.clientEmail}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="clientName">Client Name *</Label>
                  <Input
                    id="clientName"
                    value={formData.clientName}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        clientName: e.target.value,
                      }))
                    }
                    placeholder="Enter client name"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="clientPhone">Phone Number *</Label>
                  <Input
                    id="clientPhone"
                    value={formData.clientPhone}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        clientPhone: e.target.value,
                      }))
                    }
                    placeholder="Enter phone number"
                    required
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="clientEmail">Email Address</Label>
                  <Input
                    id="clientEmail"
                    type="email"
                    value={formData.clientEmail}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        clientEmail: e.target.value,
                      }))
                    }
                    placeholder="Enter email address"
                  />
                </div>
              </div>
            )}
          </Card>
          {/* Service Information */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <ServiceIcon size={20} />
              Service Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="locationId">Location *</Label>
                <Select
                  value={formData.locationId}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, locationId: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue>
                      {formData.locationId
                        ? locations?.find((l) => l._id === formData.locationId)
                            ?.name || "Select a location"
                        : "Select a location"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {locationsLoading ? (
                      <SelectItem value="loading" disabled>
                        Loading locations...
                      </SelectItem>
                    ) : locations && locations.length > 0 ? (
                      locations.map((location) => (
                        <SelectItem key={location._id} value={location._id}>
                          {location.name} ({location.city}, {location.state})
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>
                        No locations available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="serviceId">Service *</Label>
                <Select
                  value={formData.serviceId}
                  onValueChange={(value) => {
                    const selectedService = services?.find(
                      (s) => s.id === value,
                    );
                    setFormData((prev) => ({
                      ...prev,
                      serviceId: value,
                      price: selectedService?.price || 0,
                      duration: selectedService?.duration_minutes || 60,
                    }));
                  }}
                >
                  <SelectTrigger>
                    <SelectValue>
                      {formData.serviceId
                        ? services?.find((s) => s.id === formData.serviceId)
                            ?.name || "Select a service"
                        : "Select a service"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {servicesLoading ? (
                      <SelectItem value="loading" disabled>
                        Loading services...
                      </SelectItem>
                    ) : services && services.length > 0 ? (
                      services.map((service) => (
                        <SelectItem key={service.id} value={service.id}>
                          {service.name} - ${service.price}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>
                        No services available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="stylistId">Stylist *</Label>
                <Select
                  value={formData.stylistId}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, stylistId: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue>
                      {formData.stylistId
                        ? stylists?.find((s) => s.id === formData.stylistId)
                            ?.name || "Select a stylist"
                        : "Select a stylist"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {stylistsLoading ? (
                      <SelectItem value="loading" disabled>
                        Loading stylists...
                      </SelectItem>
                    ) : stylists && stylists.length > 0 ? (
                      stylists.map((stylist) => (
                        <SelectItem key={stylist.id} value={stylist.id}>
                          {stylist.name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>
                        No stylists available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bookingDate">Select Date *</Label>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    {/* Simple Calendar - Always visible */}
                    <div className="grid grid-cols-7 gap-2 mb-4">
                      {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(
                        (day) => (
                          <div
                            key={day}
                            className="text-center text-sm font-medium text-gray-600 p-2"
                          >
                            {day}
                          </div>
                        ),
                      )}
                      {(() => {
                        const today = new Date();
                        const currentMonth = today.getMonth();
                        const currentYear = today.getFullYear();
                        const daysInMonth = new Date(
                          currentYear,
                          currentMonth + 1,
                          0,
                        ).getDate();
                        const firstDay = new Date(
                          currentYear,
                          currentMonth,
                          1,
                        ).getDay();
                        const days = [];

                        // Empty cells for days before month starts
                        for (let i = 0; i < firstDay; i++) {
                          days.push(
                            <div key={`empty-${i}`} className="p-2"></div>,
                          );
                        }

                        // Days of the month
                        for (let day = 1; day <= daysInMonth; day++) {
                          const date = new Date(currentYear, currentMonth, day);
                          const dateStr = date.toISOString().split("T")[0];
                          const isToday =
                            date.toDateString() === today.toDateString();
                          const isPast = date < today;
                          const isSelected = selectedDate === dateStr;
                          const canSelectDate =
                            formData.stylistId && formData.serviceId;

                          days.push(
                            <button
                              key={day}
                              onClick={() =>
                                canSelectDate && handleDateSelect(dateStr)
                              }
                              disabled={isPast || !canSelectDate}
                              className={`p-2 text-sm rounded transition-colors ${
                                isPast || !canSelectDate
                                  ? "text-gray-300 cursor-not-allowed"
                                  : isSelected
                                    ? "bg-blue-500 text-white"
                                    : isToday
                                      ? "bg-blue-100 text-blue-900 hover:bg-blue-200"
                                      : "hover:bg-gray-100"
                              }`}
                              title={
                                !canSelectDate
                                  ? "Please select a service and stylist first"
                                  : isPast
                                    ? "Past date"
                                    : `Select ${dateStr}`
                              }
                            >
                              {day}
                            </button>,
                          );
                        }

                        return days;
                      })()}
                    </div>

                    {/* Instructions or Selected Date Display */}
                    {!formData.stylistId || !formData.serviceId ? (
                      <div className="text-sm text-gray-500 text-center p-2 bg-gray-50 rounded">
                        Please select a service and stylist first to choose a
                        date
                      </div>
                    ) : selectedDate ? (
                      <div className="text-sm text-gray-600 mb-2">
                        Selected: {new Date(selectedDate).toLocaleDateString()}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500 text-center p-2">
                        Click on a date to select it
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Time Slots */}
              {selectedDate && (
                <div className="space-y-2">
                  <Label>Available Times *</Label>
                  {availabilityLoading ? (
                    <div className="p-4 text-center">
                      <Spinner size="sm" className="mr-2" />
                      Loading available times...
                    </div>
                  ) : availableSlots.length > 0 ? (
                    <div className="grid grid-cols-4 gap-2">
                      {availableSlots.map((slot) => (
                        <button
                          key={slot.timestamp}
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              bookingTime: slot.time,
                            }))
                          }
                          disabled={!slot.available}
                          className={`p-2 text-sm rounded border transition-colors ${
                            !slot.available
                              ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200"
                              : formData.bookingTime === slot.time
                                ? "bg-blue-500 text-white border-blue-500"
                                : "bg-white hover:bg-blue-50 border-gray-300 hover:border-blue-300"
                          }`}
                        >
                          {slot.time}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-gray-500 border rounded">
                      No available times for this date
                    </div>
                  )}

                  {/* Selected Time Display */}
                  {formData.bookingTime && (
                    <div className="text-sm text-green-600">
                      Selected time: {formData.bookingTime}
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>
          {/* Service Customization - NEW FEATURE */}
          {formData.serviceId && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {variants.length > 0 && (
                  <Card className="p-6">
                    <h2 className="text-lg font-semibold text-foreground mb-4">
                      Service Variants
                    </h2>
                    <VariantSelector
                      variants={variants}
                      selectedVariantId={selectedVariant}
                      onVariantSelect={(variantId) => selectVariant(variantId)}
                      basePrice={formData.price}
                      baseDuration={formData.duration}
                    />
                  </Card>
                )}

                {addOns.length > 0 && (
                  <Card className="p-6">
                    <h2 className="text-lg font-semibold text-foreground mb-4">
                      Add-On Services
                    </h2>
                    <AddOnSelector
                      addOns={addOns}
                      selectedAddOnIds={selectedAddOns}
                      onAddOnsChange={(addOnIds) => {
                        addOnIds.forEach((id) => {
                          if (!selectedAddOns.includes(id)) {
                            toggleAddOn(id);
                          }
                        });
                        selectedAddOns.forEach((id) => {
                          if (!addOnIds.includes(id)) {
                            toggleAddOn(id);
                          }
                        });
                      }}
                    />
                  </Card>
                )}
              </div>

              {/* Cost Calculator - NEW FEATURE */}
              <div className="space-y-6">
                <CostCalculator
                  subtotal={formData.price}
                  variantCost={calculatePriceModifier()}
                  creditsApplied={formData.creditsToApply}
                />

                {/* Package Credits - NEW FEATURE */}
                {creditBalance && creditBalance.balance > 0 && (
                  <Card className="p-4">
                    <h3 className="text-lg font-semibold text-foreground mb-3">
                      Package Credits
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">
                          Available:
                        </span>
                        <span className="font-medium">
                          ${creditBalance.balance.toFixed(2)}
                        </span>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="creditsToApply">Apply Credits</Label>
                        <Input
                          id="creditsToApply"
                          type="number"
                          step="0.01"
                          min="0"
                          max={Math.min(creditBalance.balance, calculatedCost)}
                          value={formData.creditsToApply}
                          onChange={(e) =>
                            setFormData((prev) => ({
                              ...prev,
                              creditsToApply: parseFloat(e.target.value) || 0,
                            }))
                          }
                          placeholder="0.00"
                        />
                      </div>
                    </div>
                  </Card>
                )}

                {/* Payment Method - NEW FEATURE */}
                <PaymentMethodSelector
                  methods={paymentMethods}
                  selectedMethod={formData.paymentMethod}
                  onMethodSelect={(methodId) =>
                    setFormData((prev) => ({
                      ...prev,
                      paymentMethod: methodId,
                    }))
                  }
                  availableCredits={creditBalance?.balance}
                />
              </div>
            </div>
          )}
          {/* Notes */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Additional Notes
            </h2>
            <Textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, notes: e.target.value }))
              }
              placeholder="Any special requests or notes..."
              rows={4}
            />
          </Card>

          {/* Enhanced Summary - NEW FEATURE */}
          {formData.serviceId && (
            <Card className="p-6 bg-accent/5">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Booking Summary
              </h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Service</span>
                  <span className="text-sm">${formData.price.toFixed(2)}</span>
                </div>
                {calculatePriceModifier() > 0 && (
                  <div className="flex justify-between">
                    <span className="text-sm">Variants & Add-ons</span>
                    <span className="text-sm">
                      +${calculatePriceModifier().toFixed(2)}
                    </span>
                  </div>
                )}
                {formData.creditsToApply > 0 && (
                  <div className="flex justify-between">
                    <span className="text-sm">Package Credits</span>
                    <span className="text-sm">
                      -${formData.creditsToApply.toFixed(2)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between font-semibold border-t pt-2">
                  <span>Total</span>
                  <span>${calculatedCost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Duration</span>
                  <span>{calculatedDuration} minutes</span>
                </div>
                {formData.paymentMethod && (
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Payment Method</span>
                    <span>
                      {
                        paymentMethods.find(
                          (m) => m.id === formData.paymentMethod,
                        )?.name
                      }
                    </span>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Submit Button */}
          <div className="flex gap-3">
            <Button
              type="button"
              onClick={() => navigate("/dashboard/bookings")}
              variant="outline"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting} className="flex-1">
              {isSubmitting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Creating Booking...
                </>
              ) : (
                <>
                  <CheckIcon size={16} className="mr-2" />
                  Create Booking
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
