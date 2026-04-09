import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { ArrowLeftIcon, CheckIcon } from "@/components/icons";
import { ServiceSelector } from "@/components/bookings/ServiceSelector";
import { AvailabilityPicker } from "@/components/bookings/AvailabilityPicker";
import { NewCustomerForm } from "@/components/bookings/NewCustomerForm";
import { useServices } from "@/hooks/useServices";
import { useStaff } from "@/hooks/useStaff";
import { useCustomers } from "@/hooks/useCustomers";
import { useCreateBooking } from "@/hooks/useBookings";
import type { Service, AvailableSlot } from "@/types";

type WizardStep =
  | "customer"
  | "service"
  | "staff"
  | "availability"
  | "confirmation";

interface BookingFormData {
  customerId?: string;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  customerMode?: "existing" | "new";
  serviceId?: string;
  staffId?: string;
  selectedSlot?: AvailableSlot;
  selectedDate?: string;
}

export default function CreateBooking() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [step, setStep] = useState<WizardStep>("customer");
  const [paymentOption, setPaymentOption] = useState<"now" | "later">("later");
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<BookingFormData>(() => {
    // Load from localStorage on mount
    const saved = localStorage.getItem("bookingFormData");
    return saved ? JSON.parse(saved) : { customerMode: "existing" };
  });
  const { data: services = [], isLoading: servicesLoading } = useServices();
  const { data: staff = [], isLoading: staffLoading } = useStaff({
    status: "active",
  });
  const { data: customersData, isLoading: customersLoading } = useCustomers();
  const customers = customersData?.customers || [];
  const { mutate: createBooking, isPending } = useCreateBooking();

  // Auto-save form data to localStorage
  const updateFormData = (updates: Partial<BookingFormData>) => {
    setFormData((prev) => {
      const updated = { ...prev, ...updates };
      localStorage.setItem("bookingFormData", JSON.stringify(updated));
      return updated;
    });
  };

  const selectedService = services.find(
    (s: Service) => s.id === formData.serviceId,
  );
  const selectedStaff = staff.find((s: any) => s.id === formData.staffId);

  const handleCustomerModeSelect = (mode: "existing" | "new") => {
    updateFormData({
      customerMode: mode,
      customerId: undefined,
      customerName: undefined,
      customerEmail: undefined,
      customerPhone: undefined,
    });
  };

  const handleExistingCustomerSelect = (customerId: string) => {
    const customer = customers.find((c: any) => c.id === customerId);
    if (customer) {
      updateFormData({
        customerId,
        customerName: `${customer.firstName} ${customer.lastName}`,
        customerEmail: customer.email,
        customerPhone: customer.phone,
        customerMode: "existing",
      });
      setStep("service");
    }
  };

  const handleNewCustomerSubmit = async (
    name: string,
    email: string,
    phone: string,
  ) => {
    try {
      // Save customer to backend immediately
      const nameParts = name.trim().split(" ");
      const firstName = nameParts[0];
      const lastName = nameParts.slice(1).join(" ") || "Guest";

      const response = await fetch("/api/v1/customers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Tenant context comes from httpOnly cookie, no need for X-Tenant-ID header
        },
        credentials: "include",
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          phone,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage =
          errorData.detail || "Failed to save customer. Please try again.";
        setError(errorMessage);
        showToast({
          variant: "error",
          title: "Error",
          description: errorMessage,
        });
        return;
      }

      const customerData = await response.json();
      const customerId = customerData.data?.id || customerData.id;

      // Update form data with the saved customer ID
      updateFormData({
        customerId,
        customerName: name,
        customerEmail: email,
        customerPhone: phone,
        customerMode: "new",
      });

      showToast({
        variant: "success",
        title: "Success",
        description: `Customer ${name} has been created successfully`,
      });

      // Refresh customers list to include the newly created customer
      // This will be picked up by the useCustomers hook
      setStep("service");
    } catch (err) {
      const errorMessage = "Failed to save customer. Please try again.";
      setError(errorMessage);
      showToast({
        variant: "error",
        title: "Error",
        description: errorMessage,
      });
      console.error("[CreateBooking] Error saving customer:", err);
    }
  };

  const handleServiceSelect = (service: Service) => {
    updateFormData({
      serviceId: service.id,
    });
    setStep("staff");
  };

  const handleStaffSelect = (staffId: string) => {
    updateFormData({
      staffId,
    });
    setStep("availability");
  };

  const handleSlotSelect = (slot: AvailableSlot) => {
    updateFormData({
      selectedSlot: slot,
    });
  };

  const handleDateSelect = (date: string) => {
    updateFormData({
      selectedDate: date,
    });
  };

  const handleContinueToConfirmation = () => {
    if (formData.selectedSlot) {
      setStep("confirmation");
    }
  };

  const handleConfirmBooking = async () => {
    console.log("[CreateBooking] handleConfirmBooking called");
    console.log("[CreateBooking] paymentOption:", paymentOption);
    console.log("[CreateBooking] formData:", {
      serviceId: formData.serviceId,
      selectedSlot: formData.selectedSlot,
      staffId: formData.staffId,
      customerId: formData.customerId,
      selectedDate: formData.selectedDate,
    });

    if (
      formData.serviceId &&
      formData.selectedSlot &&
      formData.staffId &&
      formData.customerId &&
      formData.selectedDate
    ) {
      // Send times as local timezone strings (YYYY-MM-DD and HH:MM format)
      // Backend will store and work with local times
      const startTimeStr = `${formData.selectedDate}T${formData.selectedSlot.start_time}:00`;
      const endTimeStr = `${formData.selectedDate}T${formData.selectedSlot.end_time}:00`;

      console.log("[CreateBooking] Sending appointment (local timezone):");
      console.log("  selectedDate:", formData.selectedDate);
      console.log("  start_time:", formData.selectedSlot.start_time);
      console.log("  end_time:", formData.selectedSlot.end_time);
      console.log("  startTimeStr:", startTimeStr);
      console.log("  endTimeStr:", endTimeStr);

      const bookingPayload = {
        customerId:
          formData.customerId === "new" ? undefined : formData.customerId || "",
        customerName: formData.customerName || "",
        customerEmail: formData.customerEmail || "",
        customerPhone: formData.customerPhone || "",
        serviceId: formData.serviceId || "",
        staffId: formData.staffId || "",
        startTime: startTimeStr,
        endTime: endTimeStr,
        paymentOption: paymentOption,
      };

      // If "Pay Now" is selected, redirect to payment page
      if (paymentOption === "now") {
        console.log(
          "[CreateBooking] Pay Now selected - redirecting to payment page",
        );
        // Save booking payload to localStorage for payment page
        localStorage.setItem("pendingBooking", JSON.stringify(bookingPayload));
        console.log("[CreateBooking] Saved booking payload to localStorage");
        // Redirect to booking payment page
        console.log("[CreateBooking] Navigating to /payments/booking-payment");
        navigate("/payments/booking-payment", {
          state: {
            bookingData: bookingPayload,
            amount: selectedService?.price || 0,
            description: `Booking for ${selectedService?.name}`,
          },
        });
        return;
      }

      // If "Pay Later", create booking immediately
      createBooking(bookingPayload, {
        onSuccess: (bookingData) => {
          // Clear saved form data on successful booking
          localStorage.removeItem("bookingFormData");
          setError(null);

          showToast({
            variant: "success",
            title: "Success",
            description: "Booking has been created successfully",
          });

          // Navigate to confirmation page with booking data
          navigate("/bookings/confirmation", {
            state: { booking: bookingData },
          });
        },
        onError: (error: any) => {
          const errorMessage =
            error?.response?.data?.detail ||
            error?.message ||
            "Failed to create booking. Please try again.";
          setError(errorMessage);
          showToast({
            variant: "error",
            title: "Error",
            description: errorMessage,
          });
          console.error("[CreateBooking] Error:", errorMessage);
        },
      });
    }
  };

  const handleBack = () => {
    if (step === "service") {
      setStep("customer");
      updateFormData({
        serviceId: undefined,
      });
    } else if (step === "staff") {
      setStep("service");
      updateFormData({
        staffId: undefined,
      });
    } else if (step === "availability") {
      setStep("staff");
      updateFormData({
        selectedSlot: undefined,
      });
    } else if (step === "confirmation") {
      setStep("availability");
    } else {
      navigate("/bookings");
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBack}
          className="gap-2 w-fit cursor-pointer"
          disabled={isPending}
        >
          <ArrowLeftIcon size={18} />
          Back
        </Button>
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-foreground">
            Create Booking
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Step{" "}
            {step === "customer"
              ? 1
              : step === "service"
                ? 2
                : step === "staff"
                  ? 3
                  : step === "availability"
                    ? 4
                    : 5}{" "}
            of 5
          </p>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="flex gap-2">
        <div
          className={`flex-1 h-1 rounded-full ${
            step === "customer" ||
            step === "service" ||
            step === "staff" ||
            step === "availability" ||
            step === "confirmation"
              ? "bg-primary"
              : "bg-muted"
          }`}
        />
        <div
          className={`flex-1 h-1 rounded-full ${
            step === "service" ||
            step === "staff" ||
            step === "availability" ||
            step === "confirmation"
              ? "bg-primary"
              : "bg-muted"
          }`}
        />
        <div
          className={`flex-1 h-1 rounded-full ${
            step === "staff" ||
            step === "availability" ||
            step === "confirmation"
              ? "bg-primary"
              : "bg-muted"
          }`}
        />
        <div
          className={`flex-1 h-1 rounded-full ${
            step === "availability" || step === "confirmation"
              ? "bg-primary"
              : "bg-muted"
          }`}
        />
        <div
          className={`flex-1 h-1 rounded-full ${
            step === "confirmation" ? "bg-primary" : "bg-muted"
          }`}
        />
      </div>

      {/* Content */}
      <Card className="p-6">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        {step === "customer" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Select Customer
              </h3>
              <p className="text-sm text-muted-foreground">
                Choose an existing customer or create a new one
              </p>
            </div>

            {/* Mode Selection */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              <Card
                className={`p-4 cursor-pointer transition ${
                  formData.customerMode === "existing"
                    ? "border-primary bg-primary/5"
                    : "hover:border-primary/50"
                }`}
                onClick={() => handleCustomerModeSelect("existing")}
              >
                <div className="text-center">
                  <p className="font-semibold text-foreground">
                    Existing Customer
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Select from your customer list
                  </p>
                </div>
              </Card>
              <Card
                className={`p-4 cursor-pointer transition ${
                  formData.customerMode === "new"
                    ? "border-primary bg-primary/5"
                    : "hover:border-primary/50"
                }`}
                onClick={() => handleCustomerModeSelect("new")}
              >
                <div className="text-center">
                  <p className="font-semibold text-foreground">New Customer</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Add customer information
                  </p>
                </div>
              </Card>
            </div>

            {/* Existing Customer Selection */}
            {formData.customerMode === "existing" && (
              <div className="space-y-3">
                {customersLoading ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {[...Array(3)].map((_, i) => (
                      <Card key={i} className="p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-32" />
                            <Skeleton className="h-3 w-48" />
                            <Skeleton className="h-3 w-40" />
                          </div>
                          <Skeleton className="h-5 w-5 rounded-full" />
                        </div>
                      </Card>
                    ))}
                  </div>
                ) : customers.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {customers.map((customer: any) => (
                      <Card
                        key={customer.id}
                        className={`p-3 cursor-pointer transition ${
                          formData.customerId === customer.id
                            ? "border-primary bg-primary/5"
                            : "hover:border-primary/50"
                        }`}
                        onClick={() =>
                          handleExistingCustomerSelect(customer.id)
                        }
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-sm text-foreground">
                              {customer.firstName} {customer.lastName}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {customer.email}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {customer.phone}
                            </p>
                          </div>
                          {formData.customerId === customer.id && (
                            <CheckIcon size={20} className="text-primary" />
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No customers found. Create a new customer instead.
                  </div>
                )}
              </div>
            )}

            {/* New Customer Form */}
            {formData.customerMode === "new" && (
              <NewCustomerForm onSubmit={handleNewCustomerSubmit} />
            )}
          </div>
        )}
        {step === "service" && (
          <ServiceSelector
            services={services}
            selectedServiceId={formData.serviceId}
            onServiceSelect={handleServiceSelect}
          />
        )}

        {step === "staff" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Select Staff Member
              </h3>
              <p className="text-sm text-muted-foreground">
                Choose who will provide the service
              </p>
            </div>

            {staffLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {[...Array(4)].map((_, i) => (
                  <Card
                    key={i}
                    className="p-3 sm:p-4 min-h-[80px] sm:min-h-auto"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <Skeleton className="w-12 h-12 sm:w-16 sm:h-16 rounded-full flex-shrink-0" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-40" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : staff.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {staff.map((member: any) => (
                  <Card
                    key={member.id}
                    className={`p-3 sm:p-4 cursor-pointer transition min-h-[80px] sm:min-h-auto ${
                      formData.staffId === member.id
                        ? "border-primary bg-primary/5"
                        : "hover:border-primary/50"
                    }`}
                    onClick={() => handleStaffSelect(member.id)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      {/* Staff Image */}
                      <div className="flex-shrink-0">
                        {member.profile_image_url ? (
                          <img
                            src={member.profile_image_url}
                            alt={`${member.firstName} ${member.lastName}`}
                            className="w-12 h-12 sm:w-16 sm:h-16 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-muted flex items-center justify-center">
                            <span className="text-xs sm:text-sm font-semibold text-muted-foreground">
                              {member.firstName?.[0]}
                              {member.lastName?.[0]}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Staff Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-sm sm:text-base text-foreground truncate">
                          {member.firstName} {member.lastName}
                        </h4>
                        {member.specialties &&
                          member.specialties.length > 0 && (
                            <p className="text-xs text-muted-foreground mt-1 truncate">
                              {member.specialties.join(", ")}
                            </p>
                          )}
                        {member.bio && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {member.bio}
                          </p>
                        )}
                      </div>

                      {/* Selection Indicator */}
                      {formData.staffId === member.id && (
                        <CheckIcon
                          size={20}
                          className="text-primary flex-shrink-0"
                        />
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No staff members available
              </div>
            )}

            <Button
              onClick={() => setStep("availability")}
              disabled={!formData.staffId}
              className="w-full cursor-pointer"
            >
              Continue to Time Selection
            </Button>
          </div>
        )}

        {step === "availability" && selectedService && (
          <AvailabilityPicker
            staffId={formData.staffId || ""}
            serviceId={formData.serviceId || ""}
            serviceDuration={selectedService.duration_minutes || 0}
            selectedSlot={formData.selectedSlot}
            onSlotSelect={handleSlotSelect}
            onDateSelect={handleDateSelect}
            onNext={handleContinueToConfirmation}
          />
        )}

        {step === "confirmation" &&
          selectedService &&
          formData.selectedSlot && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  Confirm Your Booking
                </h3>
              </div>

              {/* Booking Summary with Images */}
              <div className="space-y-4">
                {/* Customer Section */}
                <div className="border rounded-lg p-4 space-y-3 bg-blue-50">
                  <h4 className="font-semibold text-foreground">Customer</h4>
                  <div className="space-y-2">
                    {formData.customerName && (
                      <div>
                        <p className="text-xs text-muted-foreground">Name</p>
                        <p className="font-semibold text-foreground">
                          {formData.customerName}
                        </p>
                      </div>
                    )}
                    {formData.customerEmail && (
                      <div>
                        <p className="text-xs text-muted-foreground">Email</p>
                        <p className="font-semibold text-foreground">
                          {formData.customerEmail}
                        </p>
                      </div>
                    )}
                    {formData.customerPhone && (
                      <div>
                        <p className="text-xs text-muted-foreground">Phone</p>
                        <p className="font-semibold text-foreground">
                          {formData.customerPhone}
                        </p>
                      </div>
                    )}
                    {!formData.customerName &&
                      !formData.customerEmail &&
                      !formData.customerPhone && (
                        <p className="text-sm text-muted-foreground italic">
                          No customer details available
                        </p>
                      )}
                  </div>
                </div>

                {/* Service Section */}
                <div className="border rounded-lg p-4 space-y-3">
                  <h4 className="font-semibold text-foreground">Service</h4>
                  <div className="flex gap-4">
                    {selectedService.public_image_url ? (
                      <img
                        src={selectedService.public_image_url}
                        alt={selectedService.name}
                        className="w-20 h-20 rounded-lg object-cover"
                      />
                    ) : (
                      <div className="w-20 h-20 rounded-lg bg-muted flex items-center justify-center">
                        <span className="text-2xl">✂️</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="font-semibold text-foreground">
                        {selectedService.name}
                      </p>
                      {selectedService.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {selectedService.description}
                        </p>
                      )}
                      <div className="flex gap-4 mt-2 text-sm">
                        <span className="text-muted-foreground">
                          Duration: {selectedService.duration_minutes} min
                        </span>
                        <span className="font-semibold text-foreground">
                          ₦
                          {typeof selectedService.price === "number"
                            ? selectedService.price.toLocaleString()
                            : parseFloat(
                                String(selectedService.price),
                              ).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Staff Section */}
                <div className="border rounded-lg p-4 space-y-3">
                  <h4 className="font-semibold text-foreground">
                    Staff Member
                  </h4>
                  <div className="flex gap-4">
                    {selectedStaff?.profile_image_url ? (
                      <img
                        src={selectedStaff.profile_image_url}
                        alt={`${selectedStaff.firstName} ${selectedStaff.lastName}`}
                        className="w-20 h-20 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
                        <span className="text-lg font-semibold text-muted-foreground">
                          {selectedStaff?.firstName?.[0]}
                          {selectedStaff?.lastName?.[0]}
                        </span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="font-semibold text-foreground">
                        {selectedStaff
                          ? `${selectedStaff.firstName} ${selectedStaff.lastName}`
                          : "N/A"}
                      </p>
                      {selectedStaff?.specialties &&
                        selectedStaff.specialties.length > 0 && (
                          <p className="text-sm text-muted-foreground mt-1">
                            Specialties: {selectedStaff.specialties.join(", ")}
                          </p>
                        )}
                      {selectedStaff?.bio && (
                        <p className="text-sm text-muted-foreground mt-2">
                          {selectedStaff.bio}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Date & Time Section */}
                <div className="border rounded-lg p-4 space-y-3">
                  <h4 className="font-semibold text-foreground">Date & Time</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Date</p>
                      <p className="font-semibold text-foreground">
                        {formData.selectedDate
                          ? new Date(
                              formData.selectedDate + "T00:00:00",
                            ).toLocaleDateString("en-US", {
                              weekday: "long",
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })
                          : "No date selected"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Time</p>
                      <p className="font-semibold text-foreground">
                        {formData.selectedSlot.start_time} -{" "}
                        {formData.selectedSlot.end_time}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Payment Section */}
                <div className="border rounded-lg p-4 space-y-4 bg-primary/5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-foreground">Payment</h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Choose when to pay
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Total Amount
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        ₦
                        {typeof selectedService.price === "number"
                          ? selectedService.price.toLocaleString()
                          : parseFloat(
                              String(selectedService.price),
                            ).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Payment Options */}
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setPaymentOption("now")}
                      className={`p-3 rounded-lg border-2 transition cursor-pointer ${
                        paymentOption === "now"
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <p className="font-semibold text-sm text-foreground">
                        Pay Now
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Secure your slot
                      </p>
                    </button>
                    <button
                      onClick={() => setPaymentOption("later")}
                      className={`p-3 rounded-lg border-2 transition cursor-pointer ${
                        paymentOption === "later"
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <p className="font-semibold text-sm text-foreground">
                        Pay Later
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Pay on arrival
                      </p>
                    </button>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  disabled={isPending}
                  className="flex-1 h-11 sm:h-10 cursor-pointer"
                >
                  Back
                </Button>
                <Button
                  onClick={() => {
                    console.log(
                      "[CreateBooking] Confirm Booking button clicked",
                    );
                    handleConfirmBooking();
                  }}
                  disabled={isPending}
                  className="flex-1 h-11 sm:h-10 gap-2 cursor-pointer"
                >
                  {isPending ? "Creating..." : "Confirm Booking"}
                  {!isPending && <CheckIcon size={18} />}
                </Button>
              </div>
            </div>
          )}
      </Card>
    </div>
  );
}
