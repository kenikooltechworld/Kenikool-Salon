import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { XIcon } from "@/components/icons";
import { ServiceSelector } from "./service-selector";
import { DateTimePicker } from "./date-time-picker";
import { GuestInfoForm } from "./guest-info-form";
import { PaymentOptions } from "./payment-options";
import { BookingConfirmation } from "./booking-confirmation";
import { PromoCodeInput } from "@/components/promo-codes";
import { useBookingStore } from "@/lib/store/bookingStore";
import { useCreateBooking } from "@/lib/api/hooks/useMarketplaceQueries";
import type { PromoCodeValidation } from "@/lib/api/hooks/usePromoCodes";

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  salonId: string;
  salonName: string;
}

type Step = "service" | "datetime" | "info" | "payment" | "confirmation";

export function BookingModal({
  isOpen,
  onClose,
  salonId,
  salonName,
}: BookingModalProps) {
  const {
    currentBooking,
    currentBookingStep,
    updateCurrentBooking,
    setBookingStep,
    nextStep,
    previousStep,
    clearCurrentBooking,
  } = useBookingStore();

  const [appliedPromoCode, setAppliedPromoCode] =
    useState<PromoCodeValidation | null>(null);
  const [discountAmount, setDiscountAmount] = useState(0);

  const createBookingMutation = useCreateBooking();
  const isLoading = createBookingMutation.isPending;

  const steps: Step[] = [
    "service",
    "datetime",
    "info",
    "payment",
    "confirmation",
  ];
  const currentStepIndex = steps.indexOf(currentBookingStep);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const handleNext = () => {
    nextStep();
  };

  const handlePrevious = () => {
    previousStep();
  };

  const handleConfirmBooking = async () => {
    try {
      const response = await createBookingMutation.mutateAsync({
        salonId,
        serviceId: currentBooking?.serviceId,
        dateTime: {
          date: currentBooking?.date,
          time: currentBooking?.time,
        },
        guestInfo: currentBooking?.guestInfo,
        paymentMethod: currentBooking?.paymentMethod,
        promoCodeId: appliedPromoCode?.promo_code_id,
      });

      updateCurrentBooking({
        bookingReference: response.reference,
        status: "confirmed",
      });
      setBookingStep("confirmation");
    } catch (error) {
      console.error("Error creating booking:", error);
    }
  };

  const handleClose = () => {
    clearCurrentBooking();
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            onClick={(e) => e.stopPropagation()}
          >
            <motion.div
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              initial={{ y: 50 }}
              animate={{ y: 0 }}
              exit={{ y: 50 }}
            >
              {/* Header */}
              <div className="sticky top-0 bg-white border-b border-border p-6 flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-foreground">
                    Book Appointment
                  </h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    {salonName}
                  </p>
                </div>
                <motion.button
                  onClick={handleClose}
                  className="p-2 hover:bg-muted rounded-lg transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <XIcon size={24} />
                </motion.button>
              </div>

              {/* Progress Bar */}
              {currentBookingStep !== "confirmation" && (
                <div className="px-6 pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-foreground">
                      Step {currentStepIndex + 1} of {steps.length}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {Math.round(progress)}%
                    </span>
                  </div>
                  <motion.div
                    className="h-2 bg-muted rounded-full overflow-hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <motion.div
                      className="h-full bg-primary"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </motion.div>
                </div>
              )}

              {/* Content */}
              <div className="p-6">
                <AnimatePresence mode="wait">
                  {currentBookingStep === "service" && (
                    <motion.div
                      key="service"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <ServiceSelector
                        salonId={salonId}
                        onSelect={(service) => {
                          updateCurrentBooking({
                            serviceId: service.id,
                            serviceName: service.name,
                            stylistId: service.stylist?.id,
                            stylistName: service.stylist?.name,
                          });
                          handleNext();
                        }}
                      />
                    </motion.div>
                  )}

                  {currentBookingStep === "datetime" && (
                    <motion.div
                      key="datetime"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <DateTimePicker
                        salonId={salonId}
                        serviceId={currentBooking?.serviceId}
                        onSelect={(dateTime) => {
                          updateCurrentBooking(dateTime);
                          handleNext();
                        }}
                      />
                    </motion.div>
                  )}

                  {currentBookingStep === "info" && (
                    <motion.div
                      key="info"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <GuestInfoForm
                        onSubmit={(info) => {
                          updateCurrentBooking({ guestInfo: info });
                          handleNext();
                        }}
                      />
                    </motion.div>
                  )}

                  {currentBookingStep === "payment" && (
                    <motion.div
                      key="payment"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <div className="space-y-6">
                        <PaymentOptions
                          onSelect={(method) => {
                            updateCurrentBooking({ paymentMethod: method });
                          }}
                          selectedMethod={
                            currentBooking?.paymentMethod || "card"
                          }
                        />

                        {/* Promo Code Section */}
                        <div className="border-t pt-6">
                          <h3 className="text-lg font-semibold mb-4">
                            Apply Promo Code
                          </h3>
                          <PromoCodeInput
                            clientId={currentBooking?.guestInfo?.id || ""}
                            serviceIds={
                              currentBooking?.serviceId
                                ? [currentBooking.serviceId]
                                : []
                            }
                            totalAmount={currentBooking?.totalAmount || 0}
                            onApply={(validation) => {
                              setAppliedPromoCode(validation);
                              setDiscountAmount(
                                validation.discount_amount || 0,
                              );
                            }}
                            onClear={() => {
                              setAppliedPromoCode(null);
                              setDiscountAmount(0);
                            }}
                            appliedCode={appliedPromoCode}
                          />
                        </div>

                        {/* Price Breakdown */}
                        <div className="border-t pt-6 space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">
                              Subtotal
                            </span>
                            <span className="font-medium">
                              ${(currentBooking?.totalAmount || 0).toFixed(2)}
                            </span>
                          </div>
                          {discountAmount > 0 && (
                            <div className="flex justify-between text-sm text-green-600">
                              <span>Discount</span>
                              <span className="font-medium">
                                -${discountAmount.toFixed(2)}
                              </span>
                            </div>
                          )}
                          <div className="flex justify-between text-lg font-bold border-t pt-2">
                            <span>Total</span>
                            <span>
                              $
                              {(
                                (currentBooking?.totalAmount || 0) -
                                discountAmount
                              ).toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {currentBookingStep === "confirmation" &&
                    currentBooking?.bookingReference && (
                      <motion.div
                        key="confirmation"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                      >
                        <BookingConfirmation
                          reference={currentBooking.bookingReference}
                          salon={salonName}
                          service={currentBooking.serviceName || ""}
                          dateTime={{
                            date: currentBooking.date || "",
                            time: currentBooking.time || "",
                          }}
                        />
                      </motion.div>
                    )}
                </AnimatePresence>
              </div>

              {/* Footer */}
              {currentBookingStep !== "confirmation" && (
                <div className="border-t border-border p-6 flex gap-3 justify-end">
                  <Button
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentStepIndex === 0}
                  >
                    Previous
                  </Button>
                  <Button
                    onClick={
                      currentBookingStep === "payment"
                        ? handleConfirmBooking
                        : handleNext
                    }
                    disabled={
                      (currentBookingStep === "service" &&
                        !currentBooking?.serviceId) ||
                      (currentBookingStep === "datetime" &&
                        !currentBooking?.date) ||
                      (currentBookingStep === "info" &&
                        !currentBooking?.guestInfo) ||
                      isLoading
                    }
                    className="bg-primary hover:bg-primary-dark text-white"
                  >
                    {isLoading
                      ? "Processing..."
                      : currentBookingStep === "payment"
                        ? "Confirm Booking"
                        : "Next"}
                  </Button>
                </div>
              )}

              {currentBookingStep === "confirmation" && (
                <div className="border-t border-border p-6 flex gap-3 justify-end">
                  <Button
                    onClick={handleClose}
                    className="bg-primary hover:bg-primary-dark text-white"
                  >
                    Done
                  </Button>
                </div>
              )}
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
