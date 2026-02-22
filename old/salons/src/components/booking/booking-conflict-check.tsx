/**
 * BookingConflictCheck Component
 * Integrates conflict detection into the booking wizard
 * Validates: Requirements 2.1, 2.2, 2.3
 */
import React, { useState } from "react";
import { ConflictDetector } from "./conflict-detector";
import type { AvailabilitySlot } from "@/lib/types/booking-enhancement";

interface BookingConflictCheckProps {
  stylistId: string;
  serviceId: string;
  selectedDate: string;
  selectedTime: string;
  onConflictDetected: (hasConflict: boolean) => void;
  onAlternativesFound?: (alternatives: AvailabilitySlot[]) => void;
  children?: React.ReactNode;
}

/**
 * Component that wraps booking time selection with conflict detection
 * Prevents booking if conflict is detected and suggests alternatives
 */
export const BookingConflictCheck: React.FC<BookingConflictCheckProps> = ({
  stylistId,
  serviceId,
  selectedDate,
  selectedTime,
  onConflictDetected,
  onAlternativesFound,
  children,
}) => {
  const [hasConflict, setHasConflict] = useState(false);
  const [alternatives, setAlternatives] = useState<AvailabilitySlot[]>([]);

  // Construct start and end times from date and time
  const startTime =
    selectedDate && selectedTime ? `${selectedDate}T${selectedTime}` : "";
  // Assume 1 hour duration for now (this should come from service duration)
  const endTime =
    selectedDate && selectedTime
      ? new Date(
          new Date(`${selectedDate}T${selectedTime}`).getTime() +
            60 * 60 * 1000,
        )
          .toISOString()
          .slice(0, 19)
      : "";

  const handleConflictDetected = (conflict: boolean) => {
    setHasConflict(conflict);
    onConflictDetected(conflict);
  };

  const handleAlternativesFound = (alts: AvailabilitySlot[]) => {
    setAlternatives(alts);
    onAlternativesFound?.(alts);
  };

  // Only check for conflicts if we have all required data
  if (!stylistId || !serviceId || !startTime || !endTime) {
    return <>{children}</>;
  }

  return (
    <div className="space-y-4">
      {/* Conflict Detection Component */}
      <ConflictDetector
        stylistId={stylistId}
        serviceId={serviceId}
        startTime={startTime}
        endTime={endTime}
        onConflictDetected={handleConflictDetected}
        onAlternativesFound={handleAlternativesFound}
      />

      {/* Children (time slot picker, etc.) */}
      {children}

      {/* Conflict Status */}
      {hasConflict && alternatives.length > 0 && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <p className="text-sm text-blue-900">
            <strong>Tip:</strong> Consider booking one of the suggested
            alternative times above.
          </p>
        </div>
      )}
    </div>
  );
};

export default BookingConflictCheck;
