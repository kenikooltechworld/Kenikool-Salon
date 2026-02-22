import { useState, useMemo } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import {
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  AlertCircleIcon,
  Loader2Icon,
} from "@/components/icons";

// Import all booking components
import { AvailabilityCalendar } from "./availability-calendar";
import { TimeSlotPicker } from "./time-slot-picker";
import { ConflictDetector } from "./conflict-detector";
import { PaymentMethodSelector } from "./payment-method-selector";
import { CostCalculator } from "./cost-calculator";
import { PackageCreditRedemption } from "./package-credit-redemption";
import { TemplateSelector } from "./template-selector";
import { PrerequisiteChecker } from "./prerequisite-checker";
import { VariantSelector } from "./variant-selector";
import { AddOnSelector } from "./add-on-selector";
import { NotificationPreferences } from "./notification-preferences";
import { NotesAndRequestsInput } from "./notes-and-requests-input";
import { RecurringBookingForm } from "./recurring-booking-form";
import { FamilyMemberSelector } from "./family-member-selector";
import { BookingRulesDisplay } from "./booking-rules-display";
import { PaymentProcessor } from "./payment-processor";
import {
  useBookingTemplates,
  type BookingTemplate,
} from "@/lib/api/hooks/useBookingTemplates";
import { useAvailability } from "@/lib/api/hooks/useAvailability";
import { useServiceVariants } from "@/lib/api/hooks/useServiceVariants";
import { usePackageCreditBalance } from "@/lib/api/hooks/usePackageCredits";
import { useBookingRules } from "@/lib/api/hooks/useBookingRules";
import { usePaymentMethods } from "@/lib/api/hooks/usePaymentMethods";
import type { TimeSlot } from "@/lib/api/types";

interface PaymentMethodOption {
  id: string;
  type: "credit_card" | "debit_card" | "digital_wallet" | "package_credits";
  name: string;
  is_default?: boolean;
}

interface BookingWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  initialDate?: Date;
  serviceId?: string;
  stylistId?: string;
}

type WizardStep =
  | "template"
  | "prerequisites"
  | "availability"
  | "conflict-check"
  | "variants-addons"
  | "family"
  | "recurring"
  | "payment"
  | "notifications"
  | "notes"
  | "review"
  | "confirmation";

export function BookingWizard({
  isOpen,
  onClose,
  onSuccess,
  initialDate,
  serviceId,
  stylistId,
}: BookingWizardProps) {
  const { showToast } = useToast();
  const [currentStep, setCurrentStep] = useState<WizardStep>("template");
  const [completedSteps, setCompletedSteps] = useState<Set<WizardStep>>(
    new Set(),
  );
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  // Booking state
  const [bookingData, setBookingData] = useState({
    templateId: null as string | null,
    serviceId: serviceId || null,
    stylistId: stylistId || null,
    selectedDate: initialDate || null,
    selectedTime: null as TimeSlot | null,
    variants: [] as string[],
    addOns: [] as string[],
    familyMemberId: null as string | null,
    isRecurring: false,
    recurrencePattern: null as any,
    paymentMethod: null as string | null,
    creditAmount: 0,
    notificationPreferences: {} as any,
    notes: "",
    clientName: "",
    clientPhone: "",
    clientEmail: "",
  });

  const [selectedTemplate, setSelectedTemplate] =
    useState<BookingTemplate | null>(null);
  const [conflictError, setConflictError] = useState<string | null>(null);

  const { data: templates } = useBookingTemplates();

  // Only fetch availability if date is selected
  const { data: availabilityData, isLoading: availabilityLoading } =
    useAvailability(
      {
        service_id: bookingData.serviceId || "",
        stylist_id: bookingData.stylistId || "",
        date: bookingData.selectedDate
          ? bookingData.selectedDate.toISOString().split("T")[0]
          : "",
      },
      { enabled: !!bookingData.selectedDate },
    );

  const variantsHook = useServiceVariants(bookingData.serviceId || "");
  const { data: creditsData } = usePackageCreditBalance();
  const { rules: bookingRules, loading: rulesLoading } = useBookingRules(
    bookingData.serviceId || undefined,
    bookingData.stylistId || undefined,
  );
  const { data: paymentMethodsData, isLoading: paymentMethodsLoading } =
    usePaymentMethods(bookingData.serviceId || "", {
      enabled: !!bookingData.serviceId,
    });

  // Use hook data directly
  const variants = variantsHook.variants || [];
  const addOns = variantsHook.addOns || [];
  const availableCredits = creditsData?.balance || 0;
  const paymentMethods: PaymentMethodOption[] = (
    paymentMethodsData?.methods || []
  ).map((method: string, index: number) => ({
    id: method,
    type: method as
      | "credit_card"
      | "debit_card"
      | "digital_wallet"
      | "package_credits",
    name: method.replace(/_/g, " ").toUpperCase(),
    is_default: index === 0,
  }));

  // Calculate total cost
  const totalCost = useMemo(() => {
    let total = 0;
    // Add base service cost (would come from service data)
    // Add variant costs
    if (bookingData.variants.length > 0) {
      const variant = variants.find((v) => v.id === bookingData.variants[0]);
      if (variant) total += variant.priceModifier || 0;
    }
    // Add add-ons costs
    bookingData.addOns.forEach((addOnId) => {
      const addOn = addOns.find((a) => a.id === addOnId);
      if (addOn) total += addOn.price || 0;
    });
    // Subtract credits
    total = Math.max(0, total - bookingData.creditAmount);
    return total;
  }, [
    bookingData.variants,
    bookingData.addOns,
    bookingData.creditAmount,
    variants,
    addOns,
  ]);

  const steps: { id: WizardStep; label: string; optional?: boolean }[] = [
    { id: "template", label: "Templates", optional: true },
    { id: "prerequisites", label: "Prerequisites" },
    { id: "availability", label: "Date & Time" },
    { id: "conflict-check", label: "Conflict Check" },
    { id: "variants-addons", label: "Variants & Add-ons", optional: true },
    { id: "family", label: "Family Member", optional: true },
    { id: "recurring", label: "Recurring", optional: true },
    { id: "payment", label: "Payment" },
    { id: "notifications", label: "Notifications", optional: true },
    { id: "notes", label: "Notes", optional: true },
    { id: "review", label: "Review" },
    { id: "confirmation", label: "Confirmation" },
  ];

  // Validation logic
  const validateStep = (step: WizardStep): boolean => {
    const errors: Record<string, string> = {};

    switch (step) {
      case "availability":
        if (!bookingData.selectedDate) {
          errors.availability = "Please select a date";
        }
        if (!bookingData.selectedTime) {
          errors.availability = "Please select a time slot";
        }
        break;
      case "payment":
        if (!bookingData.paymentMethod) {
          errors.payment = "Please select a payment method";
        }
        break;
      case "prerequisites":
        // Prerequisites validation is handled by PrerequisiteChecker component
        break;
      case "conflict-check":
        if (conflictError) {
          errors.conflict = conflictError;
        }
        break;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleStepComplete = () => {
    if (!validateStep(currentStep)) {
      showToast({
        title: "Validation Error",
        description:
          validationErrors[currentStep] || "Please complete this step",
        variant: "error",
      });
      return;
    }

    setCompletedSteps(new Set([...completedSteps, currentStep]));
    moveToNextStep();
  };

  const moveToNextStep = () => {
    const currentIndex = steps.findIndex((s) => s.id === currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1].id);
    }
  };

  const moveToPreviousStep = () => {
    const currentIndex = steps.findIndex((s) => s.id === currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].id);
    }
  };

  const handleClose = () => {
    setCurrentStep("template");
    setCompletedSteps(new Set());
    setBookingData({
      templateId: null,
      serviceId: serviceId || null,
      stylistId: stylistId || null,
      selectedDate: initialDate || null,
      selectedTime: null,
      variants: [],
      addOns: [],
      familyMemberId: null,
      isRecurring: false,
      recurrencePattern: null,
      paymentMethod: null,
      creditAmount: 0,
      notificationPreferences: {},
      notes: "",
      clientName: "",
      clientPhone: "",
      clientEmail: "",
    });
    onClose();
  };

  const handleSuccess = () => {
    showToast({
      title: "Booking Confirmed!",
      description: "Your booking has been successfully created.",
      variant: "success",
    });
    handleClose();
    onSuccess?.();
  };

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);
  const isLastStep = currentStepIndex === steps.length - 1;
  const isFirstStep = currentStepIndex === 0;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Book Your Appointment</DialogTitle>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              Step {currentStepIndex + 1} of {steps.length}
            </span>
            <span className="text-sm text-muted-foreground">
              {steps[currentStepIndex].label}
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{
                width: `${((currentStepIndex + 1) / steps.length) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Step Indicators */}
        <div className="flex gap-1 mb-6 overflow-x-auto pb-2">
          {steps.map((step, index) => (
            <button
              key={step.id}
              onClick={() => setCurrentStep(step.id)}
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${
                completedSteps.has(step.id)
                  ? "bg-green-500 text-white"
                  : currentStep === step.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
              }`}
              title={step.label}
            >
              {completedSteps.has(step.id) ? (
                <CheckIcon size={16} />
              ) : (
                index + 1
              )}
            </button>
          ))}
        </div>

        {/* Step Content */}
        <div className="min-h-[300px] mb-6">
          {currentStep === "template" && templates && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Select a Template (Optional)
              </h3>
              {templates.length > 0 && !selectedTemplate ? (
                <div className="space-y-2">
                  {templates.map((template: BookingTemplate) => (
                    <Card
                      key={template.id}
                      className="p-3 cursor-pointer hover:bg-accent transition-colors"
                      onClick={() => setSelectedTemplate(template)}
                    >
                      <div className="font-medium">{template.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {template.description}
                      </div>
                    </Card>
                  ))}
                </div>
              ) : null}
              {selectedTemplate && (
                <TemplateSelector
                  template={selectedTemplate}
                  onConfirm={(template) => {
                    setSelectedTemplate(template);
                    setBookingData({
                      ...bookingData,
                      templateId: template.id,
                    });
                    handleStepComplete();
                  }}
                  onBack={() => setSelectedTemplate(null)}
                />
              )}
              {!selectedTemplate && (
                <Button
                  fullWidth
                  onClick={handleStepComplete}
                  variant="outline"
                >
                  Skip Templates
                </Button>
              )}
            </div>
          )}

          {currentStep === "prerequisites" && bookingData.serviceId && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Check Prerequisites</h3>
              <PrerequisiteChecker
                serviceId={bookingData.serviceId}
                onProceed={handleStepComplete}
              />
            </div>
          )}

          {currentStep === "availability" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Select Date & Time</h3>
              {rulesLoading ? (
                <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                  <Loader2Icon size={16} className="animate-spin" />
                  <span>Loading booking rules...</span>
                </div>
              ) : (
                bookingData.serviceId && (
                  <BookingRulesDisplay
                    rules={{
                      minAdvanceBooking: bookingRules.minAdvanceBooking || 60,
                      bufferTime: bookingRules.bufferTime || 15,
                      maxCapacity: bookingRules.maxCapacity || 10,
                      capacityRemaining: bookingRules.capacityRemaining || 5,
                    }}
                  />
                )
              )}
              {availabilityLoading ? (
                <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                  <Loader2Icon size={16} className="animate-spin" />
                  <span>Loading availability...</span>
                </div>
              ) : (
                <>
                  <AvailabilityCalendar
                    availableSlots={availabilityData?.slots || []}
                    onDateSelect={(date) => {
                      setBookingData({
                        ...bookingData,
                        selectedDate: new Date(date),
                        selectedTime: null, // Reset time when date changes
                      });
                    }}
                  />
                  {bookingData.selectedDate && (
                    <TimeSlotPicker
                      slots={availabilityData?.slots || []}
                      selectedSlot={bookingData.selectedTime?.start_time}
                      onSlotSelect={(slot) => {
                        setBookingData({
                          ...bookingData,
                          selectedTime: slot,
                        });
                        handleStepComplete();
                      }}
                    />
                  )}
                </>
              )}
            </div>
          )}

          {currentStep === "conflict-check" && bookingData.selectedTime && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Checking for Conflicts</h3>
              {conflictError && (
                <div className="flex items-start gap-3 p-4 bg-destructive/10 border border-destructive rounded-lg">
                  <AlertCircleIcon
                    size={20}
                    className="text-destructive mt-0.5 flex-shrink-0"
                  />
                  <div>
                    <p className="font-medium text-destructive">
                      Conflict Detected
                    </p>
                    <p className="text-sm text-destructive/80">
                      {conflictError}
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-2"
                      onClick={() => {
                        setConflictError(null);
                        moveToPreviousStep();
                      }}
                    >
                      Choose Different Time
                    </Button>
                  </div>
                </div>
              )}
              {!conflictError && (
                <ConflictDetector
                  serviceId={bookingData.serviceId || ""}
                  stylistId={bookingData.stylistId || ""}
                  startTime={bookingData.selectedTime.start_time}
                  endTime={bookingData.selectedTime.end_time}
                  onConflictDetected={(hasConflict) => {
                    if (hasConflict) {
                      setConflictError("This time slot has a conflict");
                    } else {
                      setConflictError(null);
                      handleStepComplete();
                    }
                  }}
                />
              )}
            </div>
          )}

          {currentStep === "variants-addons" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Customize Your Service</h3>
              {bookingData.serviceId && variants.length > 0 && (
                <VariantSelector
                  variants={variants}
                  selectedVariantId={bookingData.variants[0]}
                  onVariantSelect={(variantId) => {
                    setBookingData({ ...bookingData, variants: [variantId] });
                  }}
                  basePrice={0}
                  baseDuration={30}
                />
              )}
              {bookingData.serviceId && addOns.length > 0 && (
                <AddOnSelector
                  addOns={addOns}
                  selectedAddOnIds={bookingData.addOns}
                  onAddOnsChange={(addOnIds) => {
                    setBookingData({ ...bookingData, addOns: addOnIds });
                  }}
                />
              )}
              <Button fullWidth onClick={handleStepComplete}>
                Continue
              </Button>
            </div>
          )}

          {currentStep === "family" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Select Family Member (Optional)
              </h3>
              <FamilyMemberSelector
                onMemberSelect={(memberId) => {
                  setBookingData({ ...bookingData, familyMemberId: memberId });
                  handleStepComplete();
                }}
              />
            </div>
          )}

          {currentStep === "recurring" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Make it Recurring? (Optional)
              </h3>
              <RecurringBookingForm
                onSubmit={(pattern) => {
                  setBookingData({
                    ...bookingData,
                    isRecurring: true,
                    recurrencePattern: pattern,
                  });
                  handleStepComplete();
                }}
              />
            </div>
          )}

          {currentStep === "payment" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Payment Details</h3>
              {bookingData.serviceId && (
                <>
                  <CostCalculator
                    subtotal={totalCost}
                    variantCost={0}
                    addOnsCost={0}
                    creditsApplied={bookingData.creditAmount}
                    onTotalChange={() => {}}
                  />
                  {paymentMethodsLoading ? (
                    <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                      <Loader2Icon size={16} className="animate-spin" />
                      <span>Loading payment methods...</span>
                    </div>
                  ) : (
                    <PaymentMethodSelector
                      methods={paymentMethods}
                      selectedMethod={bookingData.paymentMethod || undefined}
                      onMethodSelect={(method) => {
                        setBookingData({
                          ...bookingData,
                          paymentMethod: method,
                        });
                      }}
                      availableCredits={availableCredits}
                    />
                  )}
                  {availableCredits > 0 && (
                    <PackageCreditRedemption
                      availableCredits={availableCredits}
                      bookingTotal={totalCost}
                      onCreditsApply={(amount) => {
                        setBookingData({
                          ...bookingData,
                          creditAmount: amount,
                        });
                      }}
                      onCreditsChange={(amount) => {
                        setBookingData({
                          ...bookingData,
                          creditAmount: amount,
                        });
                      }}
                    />
                  )}
                </>
              )}
              <Button fullWidth onClick={handleStepComplete}>
                Continue
              </Button>
            </div>
          )}

          {currentStep === "notifications" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Notification Preferences
              </h3>
              <NotificationPreferences
                preferences={bookingData.notificationPreferences}
                onSave={async (prefs) => {
                  setBookingData({
                    ...bookingData,
                    notificationPreferences: prefs,
                  });
                  handleStepComplete();
                }}
              />
            </div>
          )}

          {currentStep === "notes" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Special Requests & Notes
              </h3>
              <NotesAndRequestsInput
                onNotesChange={(notes) => {
                  setBookingData({ ...bookingData, notes });
                }}
                initialValue={bookingData.notes}
              />
              <Card className="p-4 space-y-3">
                <h4 className="font-medium">Contact Information</h4>
                <Input
                  type="text"
                  placeholder="Full Name"
                  value={bookingData.clientName}
                  onChange={(e) =>
                    setBookingData({
                      ...bookingData,
                      clientName: e.target.value,
                    })
                  }
                />
                <Input
                  type="tel"
                  placeholder="Phone Number"
                  value={bookingData.clientPhone}
                  onChange={(e) =>
                    setBookingData({
                      ...bookingData,
                      clientPhone: e.target.value,
                    })
                  }
                />
                <Input
                  type="email"
                  placeholder="Email Address"
                  value={bookingData.clientEmail}
                  onChange={(e) =>
                    setBookingData({
                      ...bookingData,
                      clientEmail: e.target.value,
                    })
                  }
                />
              </Card>
              <Button fullWidth onClick={handleStepComplete}>
                Continue
              </Button>
            </div>
          )}

          {currentStep === "review" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Review Your Booking</h3>
              <div className="bg-muted p-4 rounded-lg space-y-3 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-muted-foreground">Date:</span>
                    <p className="font-medium">
                      {bookingData.selectedDate?.toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Time:</span>
                    <p className="font-medium">
                      {bookingData.selectedTime?.start_time}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Name:</span>
                    <p className="font-medium">{bookingData.clientName}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Phone:</span>
                    <p className="font-medium">{bookingData.clientPhone}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-muted-foreground">Email:</span>
                    <p className="font-medium">{bookingData.clientEmail}</p>
                  </div>
                </div>
                {bookingData.variants.length > 0 && (
                  <div className="pt-2 border-t">
                    <span className="text-muted-foreground">Variants:</span>
                    <p className="font-medium">
                      {bookingData.variants.length} selected
                    </p>
                  </div>
                )}
                {bookingData.addOns.length > 0 && (
                  <div>
                    <span className="text-muted-foreground">Add-ons:</span>
                    <p className="font-medium">
                      {bookingData.addOns.length} selected
                    </p>
                  </div>
                )}
                {bookingData.notes && (
                  <div>
                    <span className="text-muted-foreground">Notes:</span>
                    <p className="font-medium text-right max-w-xs">
                      {bookingData.notes}
                    </p>
                  </div>
                )}
                <div className="pt-2 border-t font-semibold">
                  <div className="flex justify-between">
                    <span>Total Cost:</span>
                    <span>${totalCost.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              <Button fullWidth onClick={handleStepComplete}>
                Proceed to Payment
              </Button>
            </div>
          )}

          {currentStep === "confirmation" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Complete Payment</h3>
              <PaymentProcessor
                bookingId={
                  bookingData.templateId || bookingData.serviceId || ""
                }
                amount={totalCost}
                paymentMethod={bookingData.paymentMethod || ""}
                onSuccess={handleSuccess}
              />
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex gap-3 justify-between">
          <Button
            variant="outline"
            onClick={moveToPreviousStep}
            disabled={isFirstStep}
          >
            <ChevronLeftIcon size={16} className="mr-2" />
            Back
          </Button>

          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            {!isLastStep && (
              <Button onClick={moveToNextStep}>
                Skip
                <ChevronRightIcon size={16} className="ml-2" />
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
