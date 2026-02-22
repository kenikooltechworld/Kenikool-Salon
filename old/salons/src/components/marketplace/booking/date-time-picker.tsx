import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { useSalonAvailability } from "@/lib/api/hooks/useMarketplaceQueries";
import { Spinner } from "@/components/ui/spinner";

interface DateTimePickerProps {
  salonId: string;
  serviceId?: string;
  onSelect: (dateTime: { date: string; time: string }) => void;
}

export function DateTimePicker({
  salonId,
  serviceId,
  onSelect,
}: DateTimePickerProps) {
  const [selectedDate, setSelectedDate] = React.useState<string | null>(null);
  const [selectedTime, setSelectedTime] = React.useState<string | null>(null);

  const { data: availabilityData, isLoading } = useSalonAvailability(
    salonId,
    selectedDate || "",
    serviceId || "",
  );

  const availableSlots = availabilityData?.slots || [];

  useEffect(() => {
    if (selectedDate && selectedTime) {
      onSelect({
        date: selectedDate,
        time: selectedTime,
      });
    }
  }, [selectedDate, selectedTime, onSelect]);

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

  const dates = getDates();

  const formatDate = (date: Date) => {
    return date.toISOString().split("T")[0];
  };

  const formatDateDisplay = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Select a Date</h3>
        <div className="grid grid-cols-4 gap-2 max-h-64 overflow-y-auto">
          {dates.map((date, index) => {
            const dateStr = formatDate(date);
            const isSelected = selectedDate === dateStr;
            const isToday = formatDate(new Date()) === dateStr;

            return (
              <motion.button
                key={dateStr}
                onClick={() => setSelectedDate(dateStr)}
                className={`p-3 rounded-lg border-2 transition-all text-center ${
                  isSelected
                    ? "border-[var(--primary)] bg-[var(--primary)]/5"
                    : "border-[var(--border)] hover:border-[var(--primary)]"
                } ${isToday ? "bg-[var(--muted)]" : ""}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
              >
                <p className="text-xs font-semibold text-[var(--foreground)]">
                  {formatDateDisplay(date)}
                </p>
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  {date.getDate()}
                </p>
              </motion.button>
            );
          })}
        </div>
      </div>

      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-lg font-semibold mb-4">Select a Time</h3>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Spinner />
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="grid grid-cols-3 gap-2">
              {availableSlots.map((slot, index) => (
                <motion.button
                  key={slot}
                  onClick={() => setSelectedTime(slot)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedTime === slot
                      ? "border-[var(--primary)] bg-[var(--primary)]/5"
                      : "border-[var(--border)] hover:border-[var(--primary)]"
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 + index * 0.03 }}
                >
                  <p className="font-semibold text-sm text-[var(--foreground)]">
                    {slot}
                  </p>
                </motion.button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-[var(--muted-foreground)]">
                No available slots for this date. Please select another date.
              </p>
            </div>
          )}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-[var(--muted)] p-4 rounded-lg"
      >
        <p className="text-sm text-[var(--muted-foreground)]">
          <span className="font-semibold">Selected:</span>{" "}
          {selectedDate && selectedTime
            ? `${formatDateDisplay(new Date(selectedDate))} at ${selectedTime}`
            : "No date and time selected"}
        </p>
      </motion.div>
    </div>
  );
}
