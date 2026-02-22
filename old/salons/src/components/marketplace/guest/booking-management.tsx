import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  CalendarIcon,
  ClockIcon,
  MapPinIcon,
  PhoneIcon,
  MailIcon,
  XIcon,
  EditIcon,
} from "@/components/icons";
import {
  useGuestBooking,
  useRescheduleBooking,
  useCancelBooking,
} from "@/lib/api/hooks/useMarketplaceQueries";

interface BookingManagementProps {
  magicToken: string;
  guestEmail: string;
  onBack: () => void;
}

type Action = "view" | "reschedule" | "cancel";

export function BookingManagement({
  magicToken,
  guestEmail,
  onBack,
}: BookingManagementProps) {
  const [currentAction, setCurrentAction] = useState<Action>("view");
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [cancelReason, setCancelReason] = useState("");

  const { data: booking, isLoading: isLoadingBooking } =
    useGuestBooking(magicToken);
  const rescheduleBookingMutation = useRescheduleBooking();
  const cancelBookingMutation = useCancelBooking();

  if (isLoadingBooking) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)] mx-auto mb-4"></div>
          <p className="text-[var(--muted-foreground)]">Loading your booking...</p>
        </div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">Booking not found</p>
        <Button onClick={onBack} variant="outline">
          Try Again
        </Button>
      </div>
    );
  }

  const handleReschedule = async () => {
    if (!selectedDate || !selectedTime) return;

    try {
      await rescheduleBookingMutation.mutateAsync({
        bookingReference: booking.reference,
        magicToken,
        newDate: selectedDate,
        newTime: selectedTime,
      });
      setCurrentAction("view");
      setSelectedDate(null);
      setSelectedTime(null);
    } catch (error) {
      console.error("Error rescheduling booking:", error);
    }
  };

  const handleCancel = async () => {
    if (!cancelReason.trim()) return;

    try {
      await cancelBookingMutation.mutateAsync({
        bookingReference: booking.reference,
        magicToken,
        reason: cancelReason,
      });
      setCurrentAction("view");
      setCancelReason("");
    } catch (error) {
      console.error("Error cancelling booking:", error);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getDates = () => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const formatDateDisplay = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  const formatDateForAPI = (date: Date) => {
    return date.toISOString().split("T")[0];
  };

  return (
    <div className="space-y-6">
      {/* Booking Status */}
      <motion.div
        className={`p-4 rounded-lg border-2 ${
          booking.status === "confirmed"
            ? "bg-green-50 border-green-200"
            : booking.status === "cancelled"
              ? "bg-red-50 border-red-200"
              : "bg-yellow-50 border-yellow-200"
        }`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <p className="text-sm font-semibold">
          Status:{" "}
          <span
            className={
              booking.status === "confirmed"
                ? "text-green-700"
                : booking.status === "cancelled"
                  ? "text-red-700"
                  : "text-yellow-700"
            }
          >
            {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
          </span>
        </p>
      </motion.div>

      {/* Booking Details */}
      <AnimatePresence mode="wait">
        {currentAction === "view" && (
          <motion.div
            key="view"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Booking Reference */}
            <motion.div
              className="bg-[var(--muted)] p-4 rounded-lg"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <p className="text-sm text-[var(--muted-foreground)] mb-1">
                Booking Reference
              </p>
              <p className="font-mono font-bold text-lg text-[var(--foreground)]">
                {booking.reference}
              </p>
            </motion.div>

            {/* Salon Info */}
            <motion.div
              className="space-y-3"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h3 className="font-semibold text-[var(--foreground)]">
                {booking.salon.name}
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-3 text-[var(--muted-foreground)]">
                  <MapPinIcon size={18} />
                  <span>{booking.salon.address}</span>
                </div>
                <div className="flex items-center gap-3 text-[var(--muted-foreground)]">
                  <PhoneIcon size={18} />
                  <a
                    href={`tel:${booking.salon.phone}`}
                    className="text-[var(--primary)] hover:underline"
                  >
                    {booking.salon.phone}
                  </a>
                </div>
                <div className="flex items-center gap-3 text-[var(--muted-foreground)]">
                  <MailIcon size={18} />
                  <a
                    href={`mailto:${booking.salon.email}`}
                    className="text-[var(--primary)] hover:underline"
                  >
                    {booking.salon.email}
                  </a>
                </div>
              </div>
            </motion.div>

            {/* Service & Date/Time */}
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="bg-[var(--muted)] p-4 rounded-lg">
                <p className="text-sm text-[var(--muted-foreground)] mb-2">
                  Service
                </p>
                <p className="font-semibold text-[var(--foreground)]">
                  {booking.service.name}
                </p>
                <p className="text-sm text-[var(--muted-foreground)] mt-1">
                  ₦{booking.service.price.toLocaleString()}
                </p>
              </div>

              <div className="bg-[var(--muted)] p-4 rounded-lg">
                <p className="text-sm text-[var(--muted-foreground)] mb-2">
                  Duration
                </p>
                <p className="font-semibold text-[var(--foreground)]">
                  {booking.service.duration} minutes
                </p>
              </div>
            </motion.div>

            {/* Date & Time */}
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="bg-[var(--muted)] p-4 rounded-lg">
                <div className="flex items-center gap-2 text-[var(--muted-foreground)] mb-2">
                  <CalendarIcon size={16} />
                  <span className="text-sm">Date</span>
                </div>
                <p className="font-semibold text-[var(--foreground)]">
                  {formatDate(booking.date)}
                </p>
              </div>

              <div className="bg-[var(--muted)] p-4 rounded-lg">
                <div className="flex items-center gap-2 text-[var(--muted-foreground)] mb-2">
                  <ClockIcon size={16} />
                  <span className="text-sm">Time</span>
                </div>
                <p className="font-semibold text-[var(--foreground)]">
                  {booking.time}
                </p>
              </div>
            </motion.div>

            {/* Stylist Info */}
            {booking.stylist && (
              <motion.div
                className="bg-[var(--muted)] p-4 rounded-lg"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <p className="text-sm text-[var(--muted-foreground)] mb-2">
                  Stylist
                </p>
                <p className="font-semibold text-[var(--foreground)]">
                  {booking.stylist.name}
                </p>
              </motion.div>
            )}

            {/* Action Buttons */}
            {booking.status === "confirmed" && (
              <motion.div
                className="flex gap-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Button
                  onClick={() => setCurrentAction("reschedule")}
                  variant="outline"
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  <EditIcon size={18} />
                  Reschedule
                </Button>
                <Button
                  onClick={() => setCurrentAction("cancel")}
                  variant="outline"
                  className="flex-1 flex items-center justify-center gap-2 text-red-600 hover:text-red-700"
                >
                  <XIcon size={18} />
                  Cancel
                </Button>
              </motion.div>
            )}

            {/* Back Button */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <Button onClick={onBack} variant="outline" className="w-full">
                Back to Login
              </Button>
            </motion.div>
          </motion.div>
        )}

        {currentAction === "reschedule" && (
          <motion.div
            key="reschedule"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <h3 className="text-lg font-semibold text-[var(--foreground)]">
              Reschedule Your Appointment
            </h3>

            {/* Date Selection */}
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-3">
                Select New Date
              </label>
              <div className="grid grid-cols-4 gap-2 max-h-64 overflow-y-auto">
                {getDates().map((date) => {
                  const dateStr = formatDateForAPI(date);
                  const isSelected = selectedDate === dateStr;

                  return (
                    <motion.button
                      key={dateStr}
                      onClick={() => setSelectedDate(dateStr)}
                      className={`p-3 rounded-lg border-2 transition-all text-center ${
                        isSelected
                          ? "border-[var(--primary)] bg-[var(--primary)]/5"
                          : "border-[var(--border)] hover:border-[var(--primary)]"
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <p className="text-xs font-semibold text-[var(--foreground)]">
                        {formatDateDisplay(date)}
                      </p>
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Time Selection */}
            {selectedDate && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <label className="block text-sm font-medium text-[var(--foreground)] mb-3">
                  Select New Time
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    "09:00",
                    "10:00",
                    "11:00",
                    "14:00",
                    "15:00",
                    "16:00",
                    "17:00",
                    "18:00",
                  ].map((time) => (
                    <motion.button
                      key={time}
                      onClick={() => setSelectedTime(time)}
                      className={`p-3 rounded-lg border-2 transition-all ${
                        selectedTime === time
                          ? "border-[var(--primary)] bg-[var(--primary)]/5"
                          : "border-[var(--border)] hover:border-[var(--primary)]"
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <p className="font-semibold text-sm text-[var(--foreground)]">
                        {time}
                      </p>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                onClick={() => setCurrentAction("view")}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleReschedule}
                disabled={!selectedDate || !selectedTime || rescheduleBookingMutation.isPending}
                className="flex-1 bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white"
              >
                {rescheduleBookingMutation.isPending ? "Updating..." : "Confirm"}
              </Button>
            </div>
          </motion.div>
        )}

        {currentAction === "cancel" && (
          <motion.div
            key="cancel"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <h3 className="text-lg font-semibold text-[var(--foreground)]">
              Cancel Your Appointment
            </h3>

            {/* Warning */}
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <p className="text-sm text-red-800">
                <span className="font-semibold">⚠️ Warning:</span> Cancelling
                your appointment cannot be undone. Please make sure you want to
                proceed.
              </p>
            </div>

            {/* Reason */}
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                Reason for Cancellation (Optional)
              </label>
              <textarea
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="Tell us why you're cancelling..."
                rows={4}
                className="w-full px-4 py-2 rounded-lg border-2 border-[var(--border)] focus:border-[var(--primary)] focus:outline-none transition-colors resize-none"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                onClick={() => setCurrentAction("view")}
                variant="outline"
                className="flex-1"
              >
                Keep Appointment
              </Button>
              <Button
                onClick={handleCancel}
                disabled={cancelBookingMutation.isPending}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                {cancelBookingMutation.isPending ? "Cancelling..." : "Cancel Appointment"}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
